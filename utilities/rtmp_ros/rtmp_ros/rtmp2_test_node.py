#!/usr/bin/env python3
"""
rtmp2_test_node.py

Minimal test script for rtmp2sink (gst-plugins-bad ≥ 1.20).

Why bother: rtmp2sink was written from scratch on GIO sockets specifically to
replace librtmp's blocking behaviour.  Key differences vs the production node:

  - timeout     is a native GStreamer property (default 5 s), no librtmp hacks
  - async-connect=true (default): the TCP connect happens off the data thread,
                  so a missing server never stalls frame ingestion
  - sync=false   required for a live push source (no pipeline clock to sync to)

Only CPU encoding (x264enc) is used here — the purpose is to validate sink
connectivity and reconnect behaviour, not encoder performance.

On Jetson: nvv4l2h264enc (GPU) is tried first; falls back to x264enc (CPU).

Verify the element is present first:
  gst-inspect-1.0 rtmp2sink

Usage:
  ros2 run rtmp_ros rtmp2_test_node --ros-args \
    -p image_topic:=/camera/image_raw/compressed \
    -p url:=rtmp://myserver:1935/live/stream

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


class Rtmp2TestNode(Node):
    def __init__(self):
        super().__init__("rtmp2_test_node")

        self.declare_parameter("image_topic", "/camera/image_raw/compressed")
        self.declare_parameter("url",         "rtmp://localhost:1935/live/test")
        self.declare_parameter("bitrate",     2_000_000)
        self.declare_parameter("output_width", 0)

        self._url          = self.get_parameter("url").value
        self._bitrate      = self.get_parameter("bitrate").value
        self._output_width = self.get_parameter("output_width").value

        self._pipeline = None
        self._appsrc   = None

        topic = self.get_parameter("image_topic").value
        self._is_compressed = topic.endswith("/compressed")
        if self._is_compressed:
            self.create_subscription(CompressedImage, topic, self._on_compressed,
                                     qos_profile_sensor_data)
        else:
            self.create_subscription(Image, topic, self._on_raw,
                                     qos_profile_sensor_data)

        self.get_logger().info(f"rtmp2 test node ready. {topic} → {self._url}")

    # ── Pipeline ──────────────────────────────────────────────────────────────

    def _build_pipeline(self, src_w: int, src_h: int):
        if self._pipeline is not None:
            return

        if self._output_width > 0:
            out_w = self._output_width
            out_h = int(src_h * out_w / src_w) & ~1  # force even
        else:
            out_w, out_h = src_w, src_h

        if self._is_compressed:
            appsrc_caps = "image/jpeg"
            decode      = "! jpegdec "
        else:
            appsrc_caps = (
                f"video/x-raw,format=BGR,width={src_w},height={src_h},framerate=0/1"
            )
            decode = ""

        appsrc = (
            # Leaky appsrc queue: drop oldest frame instead of accumulating when
            # the sink is reconnecting.  leaky-type requires GStreamer ≥ 1.20.
            f"appsrc name=src is-live=true do-timestamp=true format=time "
            f"max-buffers=2 max-bytes=0 max-time=0 leaky-type=downstream "
            f"caps={appsrc_caps}"
        )

        # Belt-and-braces queue before the decoder: frames are discarded as
        # cheap compressed bytes before any decode work is wasted on them.
        leaky_queue = "! queue max-size-buffers=2 max-size-bytes=0 max-size-time=0 leaky=downstream "

        # rtmp2sink: timeout defaults to 5 s; async-connect defaults to true.
        # sync=false: don't drop frames trying to match a pipeline clock on a
        # live source that has no meaningful clock to sync to.
        rtmp_tail = (
            f"! h264parse config-interval=-1 "
            f"! video/x-h264,stream-format=avc,alignment=au "
            f"! flvmux streamable=true "
            f'! rtmp2sink location="{self._url}" sync=false'
        )

        jetson_pipe = (
            f"{appsrc} "
            f"{leaky_queue}"
            f"{decode}! videoconvert ! video/x-raw,format=BGRx "
            f"! nvvidconv "
            f"! video/x-raw(memory:NVMM),format=NV12,width={out_w},height={out_h} "
            f"! nvv4l2h264enc bitrate={self._bitrate} preset-level=1 insert-sps-pps=true "
            f"{rtmp_tail}"
        )

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
                if self._pipeline.set_state(Gst.State.PLAYING) == Gst.StateChangeReturn.FAILURE:
                    raise RuntimeError(f"{label} pipeline failed to start")
                # Only watch for ERROR — not EOS.  EOS is never expected on a live
                # push source, and connecting it would introduce a stale-callback
                # race: set_state(NULL) posts EOS on the old bus; if a new pipeline
                # was already rebuilt by the ROS callback, that stale EOS kills it.
                bus = self._pipeline.get_bus()
                bus.add_signal_watch()
                bus.connect("message::error", self._on_bus_error)
                self.get_logger().info(
                    f"[{label}] {src_w}x{src_h} → {out_w}x{out_h}, "
                    f"{self._bitrate // 1000} kbps → {self._url}"
                )
                return
            except Exception as e:
                self.get_logger().warn(f"{label} failed: {e}")
                if self._pipeline:
                    self._pipeline.set_state(Gst.State.NULL)
                self._pipeline = None

        raise RuntimeError("No H.264 encoder available (tried nvv4l2h264enc, x264enc)")

    # ── Bus ───────────────────────────────────────────────────────────────────

    def _on_bus_error(self, bus, message):
        err, debug = message.parse_error()
        self.get_logger().warn(f"GStreamer error: {err} — {debug}; reconnecting on next frame")
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)
        self._pipeline = None
        self._appsrc   = None

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_compressed(self, msg: CompressedImage):
        if self._pipeline is None:
            frame = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                return
            h, w = frame.shape[:2]
            self._build_pipeline(w, h)
        if self._appsrc is None:
            return
        buf = Gst.Buffer.new_wrapped(bytes(msg.data))
        buf.set_flags(Gst.BufferFlags.LIVE)
        self._appsrc.emit("push-buffer", buf)

    def _on_raw(self, msg: Image):
        if self._pipeline is None:
            try:
                self._build_pipeline(msg.width, msg.height)
            except RuntimeError as e:
                self.get_logger().warn(str(e))
                return
        if self._appsrc is None:
            return
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
        if msg.encoding == "rgb8":
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        buf = Gst.Buffer.new_wrapped(frame.tobytes())
        buf.set_flags(Gst.BufferFlags.LIVE)
        self._appsrc.emit("push-buffer", buf)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def destroy_node(self):
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)
        super().destroy_node()


def main():
    rclpy.init()
    node = Rtmp2TestNode()
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
