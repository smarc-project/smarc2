#!/usr/bin/env python3
import threading

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class UdpH264CameraNode(Node):
    def __init__(self):
        super().__init__('udp_h264_camera_node')

        self.declare_parameter('port', 5600)
        self.declare_parameter('frame_id', 'camera_optical_frame')
        self.declare_parameter('topic', 'image_raw')

        port = self.get_parameter('port').value
        self.frame_id = self.get_parameter('frame_id').value
        topic = self.get_parameter('topic').value

        self.publisher = self.create_publisher(Image, topic, 10)

        Gst.init(None)
        pipeline_str = (
            f'udpsrc port={port} ! application/x-rtp,payload=96 ! '
            'rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! '
            'video/x-raw,format=BGR ! appsink name=sink emit-signals=true '
            'sync=false max-buffers=1 drop=true'
        )
        self.pipeline = Gst.parse_launch(pipeline_str)
        sink = self.pipeline.get_by_name('sink')
        sink.connect('new-sample', self.on_new_sample)
        self.pipeline.set_state(Gst.State.PLAYING)

        self.loop = GLib.MainLoop()
        self.glib_thread = threading.Thread(target=self.loop.run, daemon=True)
        self.glib_thread.start()

        self.get_logger().info(f'Listening on UDP :{port}, publishing to "{topic}"')

    def on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        buf = sample.get_buffer()
        caps = sample.get_caps().get_structure(0)
        width = caps.get_value('width')
        height = caps.get_value('height')

        ok, mapinfo = buf.map(Gst.MapFlags.READ)
        if not ok:
            return Gst.FlowReturn.ERROR

        frame = np.ndarray((height, width, 3), dtype=np.uint8, buffer=mapinfo.data)

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.height = height
        msg.width = width
        msg.encoding = 'bgr8'
        msg.is_bigendian = 0
        msg.step = width * 3
        msg.data = frame.tobytes()
        self.publisher.publish(msg)

        buf.unmap(mapinfo)
        return Gst.FlowReturn.OK

    def destroy_node(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loop.quit()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UdpH264CameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()