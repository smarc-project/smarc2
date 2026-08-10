#!/usr/bin/env python3
"""
rtmp_ros_node.py

Subscribes to a ROS 2 Image or CompressedImage (JPEG) topic and streams
H.264/FLV to an RTMP server via GStreamer.

Supported image types:
  CompressedImage  — JPEG only (topic name must end with /compressed)
  Image            — bgr8 or rgb8 encoding

On Jetson: nvv4l2h264enc (GPU) is tried first; falls back to x264enc (CPU).

Parameters:
  image_topic   (str)  : ROS topic                             [default: /camera/image_raw/compressed]
  url           (str)  : RTMP ingest URL                       [default: rtmp://localhost:1935/live/test]
  bitrate       (int)  : encoder bitrate in bps                [default: 2000000]
  output_width  (int)  : output width; 0 = no resize           [default: 0]

Usage:
  ros2 run rtmp_ros rtmp_ros_node --ros-args \\
    -p image_topic:=/camera/image_raw/compressed \\
    -p url:=rtmp://myserver:1935/live/stream

  ros2 launch rtmp_ros rtmp.launch.py \\
    image_topic:=/camera/image_raw/compressed \\
    url:=rtmp://myserver:1935/live/stream

Receive:
  ffplay rtmp://myserver:1935/live/stream
"""

import threading

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from rclpy.qos import qos_profile_sensor_data
import numpy as np
import cv2

Gst.init(None)


class RtmpRosNode(Node):
    def __init__(self):
        super().__init__("rtmp_ros_node")

        self.declare_parameter("image_topic",  "/camera/image_raw/compressed")
        self.declare_parameter("url",          "rtmp://localhost:1935/live/test")
        self.declare_parameter("bitrate",      2_000_000)
        self.declare_parameter("output_width", 0)

        self._url          = self.get_parameter("url").value
        self._bitrate      = self.get_parameter("bitrate").value
        self._output_width = self.get_parameter("output_width").value

        self._pipeline = None
        self._appsrc   = None

        topic = self.get_parameter("image_topic").value
        self._is_compressed = topic.endswith("/compressed")
        # BEST_EFFORT (sensor-data profile): the DDS middleware drops frames it
        # cannot deliver immediately rather than buffering them.  With the default
        # RELIABLE policy every camera frame is queued in the DDS layer whenever
        # the ROS callback is slow, which independently fills RAM on network loss.
        if self._is_compressed:
            self.create_subscription(CompressedImage, topic, self._on_compressed,
                                     qos_profile_sensor_data)
        else:
            self.create_subscription(Image, topic, self._on_raw,
                                     qos_profile_sensor_data)

        self.get_logger().info(f"RTMP node ready. {topic} → {self._url}")

    # ── Pipeline init (lazy, triggered on first frame) ────────────────────────

    def _ensure_encoder(self, src_w: int, src_h: int):
        if self._pipeline is not None:
            return

        # Output resolution — derive height to preserve aspect ratio.
        if self._output_width > 0:
            out_w = self._output_width
            out_h = int(src_h * out_w / src_w) & ~1  # force even
        else:
            out_w, out_h = src_w, src_h

        if self._is_compressed:
            # Push raw JPEG bytes; GStreamer decodes inside the pipeline.
            appsrc_caps = "image/jpeg"
            decode = "! jpegdec "
        else:
            appsrc_caps = (
                f"video/x-raw,format=BGR,"
                f"width={src_w},height={src_h},"
                f"framerate=0/1"
            )
            decode = ""

        # max-bytes=1000 was the original limit but with block=False (default)
        # it only fires the "enough-data" signal — it does NOT drop or block.
        # max-buffers + leaky-type (GStreamer ≥ 1.20, present on JetPack 6 /
        # L4T 36.4) make the appsrc itself discard the oldest queued frame when
        # full.  Verify with: gst-inspect-1.0 appsrc | grep -A2 leaky-type
        appsrc = (
            f"appsrc name=src is-live=true do-timestamp=true format=time "
            f"min-latency=0 max-latency=0 "
            f"max-buffers=2 max-bytes=0 max-time=0 leaky-type=downstream "
            f"caps={appsrc_caps}"
        )

        # timeout=5 is a librtmp option passed through the location string.
        # Without it rtmpsink blocks indefinitely on a half-open TCP connection
        # (OS-level keepalive can take minutes), stalling the whole pipeline
        # before any of the leaky-queue limits even get a chance to help.
        rtmp_tail = (
            f"! h264parse config-interval=-1 "
            f"! video/x-h264,stream-format=avc,alignment=au "
            f"! flvmux streamable=true "
            f'! rtmpsink location="{self._url} live=1 timeout=5"'
        )

        # Belt-and-braces leaky queue placed *before* the decoder so frames are
        # discarded as raw compressed bytes — no wasted decode work on frames that
        # will never reach the encoder.  leaky=downstream drops the oldest buffered
        # frame when the queue is full.  Always drop before the encoder: discarding
        # H.264 mid-GOP corrupts the stream for every downstream decoder.
        leaky_queue = "! queue max-size-buffers=2 max-size-bytes=0 max-size-time=0 leaky=downstream "

        # Jetson HW path.
        jetson_pipe = (
            f"{appsrc} "
            f"{leaky_queue}"
            f"{decode}! videoconvert ! video/x-raw,format=BGRx "
            f"! nvvidconv "
            f"! video/x-raw(memory:NVMM),format=NV12,width={out_w},height={out_h} "
            f"! nvv4l2h264enc bitrate={self._bitrate} preset-level=1 insert-sps-pps=true "
            f"{rtmp_tail}"
        )

        # CPU fallback.
        cpu_pipe = (
            f"{appsrc} "
            f"{leaky_queue}"
            f"{decode}! videoconvert ! video/x-raw,format=I420 "
            f"! videoscale ! video/x-raw,width={out_w},height={out_h} "
            f"! x264enc bitrate={self._bitrate // 1000} tune=zerolatency speed-preset=ultrafast "
            f"{rtmp_tail}"
        )

        for label, pipe_str in [("Jetson HW", jetson_pipe), ("CPU SW", cpu_pipe)]:
            try:
                self._pipeline = Gst.parse_launch(pipe_str)
                self._appsrc   = self._pipeline.get_by_name("src")
                # set_state() returns a status enum, not an exception — check it.
                # The try/except above only catches parse failures (missing element),
                # not runtime failures like a missing NV encoder.
                if self._pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
                    raise RuntimeError(f"{label} pipeline failed to start")
                # Watch for runtime errors (network drop, encoder crash, etc.).
                # Without this, errors are silently swallowed: _pipeline stays
                # non-None and _ensure_encoder never reinitialises it.
                bus = self._pipeline.get_bus()
                bus.add_signal_watch()
                # Only connect ERROR, not EOS.  EOS is never expected on a live
                # push source.  Connecting it would cause the EOS that GStreamer
                # posts during set_state(NULL) teardown to fire the handler
                # again — potentially on a freshly rebuilt pipeline.
                bus.connect("message::error", self._on_bus_error)
                self.get_logger().info(
                    f"[{label}] {src_w}x{src_h} → {out_w}x{out_h}, "
                    f"{self._bitrate // 1000} kbps → {self._url}"
                )
                return
            except Exception as e:
                self.get_logger().warn(f"{label} failed: {e}")
                # Call set_state(NULL) before dropping the reference.  If
                # set_state(PLAYING) returned ASYNC and the exception was raised
                # afterwards, the pipeline is already transitioning to PLAYING;
                # releasing the Python reference without NULL-ing it first causes
                # GStreamer to dispose elements while they are still in PLAYING
                # state — triggering the segfault we saw.
                if self._pipeline:
                    self._pipeline.set_state(Gst.State.NULL)
                self._pipeline = None

        raise RuntimeError("No H.264 encoder available (tried nvv4l2h264enc, x264enc)")

    # ── GStreamer bus ──────────────────────────────────────────────────────────

    def _on_bus_error(self, bus, message):
        """Tear down the broken pipeline; the next frame triggers a clean rebuild."""
        err, debug = message.parse_error()
        self.get_logger().warn(f"GStreamer error: {err} — {debug}")
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)
        self._pipeline = None
        self._appsrc   = None

    # ── Frame push ────────────────────────────────────────────────────────────

    def _push_frame(self, frame: np.ndarray):
        h, w = frame.shape[:2]
        self._ensure_encoder(w, h)
        if self._appsrc is None:  # _ensure_encoder failed or lost a race with _on_bus_error
            return
        buf = Gst.Buffer.new_wrapped(frame.tobytes())
        buf.set_flags(Gst.BufferFlags.LIVE)
        self._appsrc.emit("push-buffer", buf)

    # ── ROS callbacks ─────────────────────────────────────────────────────────

    def _on_compressed(self, msg: CompressedImage):
        if self._pipeline is None:
            # One-time decode to learn source dimensions for output scaling.
            frame = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                return
            h, w = frame.shape[:2]
            self._ensure_encoder(w, h)
        if self._appsrc is None:  # _ensure_encoder failed or lost a race with _on_bus_error
            return
        buf = Gst.Buffer.new_wrapped(bytes(msg.data))
        buf.set_flags(Gst.BufferFlags.LIVE)
        self._appsrc.emit("push-buffer", buf)

    def _on_raw(self, msg: Image):
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
        if msg.encoding == "rgb8":
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self._push_frame(frame)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def destroy_node(self):
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)
        super().destroy_node()


def main():
    rclpy.init()
    node = RtmpRosNode()
    loop = GLib.MainLoop()
    threading.Thread(target=loop.run, daemon=True).start()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        loop.quit()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
