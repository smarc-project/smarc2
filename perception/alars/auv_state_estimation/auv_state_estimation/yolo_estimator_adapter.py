#!/usr/bin/env python3

import math
import os
import yaml

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PolygonStamped, Point32
from std_msgs.msg import Bool
from std_srvs.srv import Trigger

from yolo_msgs.msg import DetectionArray
from dji_msgs.msg import Links, Topics


class YoloEstimatorAdapter(Node):
    """
    Single multi-object adapter from yolo_ros DetectionArray to EKF PolygonStamped inputs.

    It subscribes only to yolo_ros detections.

    It reads object_estimation.yaml and creates one PolygonStamped publisher per object.

    Example:
      YOLO class "sam"  -> /M350/alars_detection/auv_obb
      YOLO class "buoy" -> /M350/alars_detection/buoy_obb
    """

    def __init__(self):
        super().__init__("yolo_estimator_adapter")

        self.declare_parameter("robot_name", "M350")
        self.declare_parameter("object_config_file", "")
        self.declare_parameter("camera_calibration_file", "")
        self.declare_parameter("topics.yolo_detections", "yolo/detections")
        self.declare_parameter("frames.camera", Links.GIMBAL_OPTICAL_FRAME)
        self.declare_parameter("yolo_msg_timeout", 5.0)
        self.declare_parameter("default_confidence_threshold", 0.5)

        self.robot_name = self.get_str("robot_name").strip("/")
        self.object_config_file = self.get_str("object_config_file")
        self.camera_calibration_file = self.get_str("camera_calibration_file")
        self.yolo_msg_timeout = self.get_float("yolo_msg_timeout")
        self.default_confidence_threshold = self.get_float(
            "default_confidence_threshold"
        )

        if self.robot_name == "":
            self.robot_name = self.get_namespace().strip("/")

        if self.robot_name == "":
            self.robot_name = "M350"

        if self.object_config_file == "":
            raise RuntimeError("object_config_file must be set")

        if self.camera_calibration_file == "":
            raise RuntimeError("camera_calibration_file must be set")

        self.image_width, self.image_height = self.load_image_size(
            self.camera_calibration_file
        )

        camera_frame = self.get_str("frames.camera")
        self.camera_frame = self.resolve_frame(camera_frame)

        yolo_detections_topic = self.resolve_topic(
            self.get_str("topics.yolo_detections")
        )

        self.detector_enabled = True
        self.last_yolo_msg_time = None

        self.objects = self.load_objects(self.object_config_file)
        self.object_publishers = {}

        for object_name, cfg in self.objects.items():
            self.object_publishers[object_name] = self.create_publisher(
                PolygonStamped,
                cfg["input_polygon"],
                10,
            )

        self.cam_processor_happy_pub = self.create_publisher(
            Bool,
            self.resolve_topic(Topics.CAM_PROCESSOR_HAPPY_TOPIC),
            10,
        )

        self.create_subscription(
            DetectionArray,
            yolo_detections_topic,
            self.detections_cb,
            10,
        )

        self.create_timer(
            1.0,
            self.publish_cam_processor_happy,
        )

        self.create_service(
            Trigger,
            self.resolve_topic(Topics.ENABLE_ALARS_DETECTOR_SERVICE_TOPIC),
            self.handle_enable_detector,
        )

        self.create_service(
            Trigger,
            self.resolve_topic(Topics.DISABLE_ALARS_DETECTOR_SERVICE_TOPIC),
            self.handle_disable_detector,
        )

        self.get_logger().info("Multi-object YOLO estimator adapter started")
        self.get_logger().info(f"Subscribing detections: {yolo_detections_topic}")
        self.get_logger().info(
            f"Using image size: {self.image_width}x{self.image_height}"
        )
        self.get_logger().info(f"Camera frame: {self.camera_frame}")
        self.get_logger().info("Configured object outputs:")

        for object_name, cfg in self.objects.items():
            self.get_logger().info(
                f"  {object_name}: class_name={cfg['class_name']}, "
                f"class_id={cfg['class_id']}, "
                f"threshold={cfg['confidence_threshold']}, "
                f"topic={cfg['input_polygon']}"
            )

    def get_str(self, name):
        return self.get_parameter(name).get_parameter_value().string_value

    def get_float(self, name):
        return self.get_parameter(name).get_parameter_value().double_value

    def resolve_topic(self, topic):
        topic = str(topic).strip()

        if topic.startswith("/"):
            return topic

        return f"/{self.robot_name}/{topic}"

    def resolve_frame(self, frame):
        frame = str(frame).strip("/")

        if frame.startswith(f"{self.robot_name}/"):
            return frame

        return f"{self.robot_name}/{frame}"

    def default_input_polygon_for_object(self, object_name):
        if object_name == "sam":
            return Topics.ESTIMATED_AUV_OBB_TOPIC

        if object_name == "buoy":
            return Topics.ESTIMATED_BUOY_OBB_TOPIC

        return f"alars_detection/{object_name}_obb"

    @staticmethod
    def load_image_size(camera_calibration_file):
        if not os.path.exists(camera_calibration_file):
            raise RuntimeError(
                f"camera_calibration_file does not exist: {camera_calibration_file}"
            )

        with open(camera_calibration_file, "r") as f:
            camera_config = yaml.safe_load(f) or {}

        image_width = int(
            camera_config.get("image_width", camera_config.get("width", 0))
        )
        image_height = int(
            camera_config.get("image_height", camera_config.get("height", 0))
        )

        if image_width <= 0 or image_height <= 0:
            raise RuntimeError(
                f"Could not read image_width/image_height from {camera_calibration_file}"
            )

        return image_width, image_height

    def load_objects(self, object_config_file):
        if not os.path.exists(object_config_file):
            raise RuntimeError(
                f"object_config_file does not exist: {object_config_file}"
            )

        with open(object_config_file, "r") as f:
            object_config = yaml.safe_load(f) or {}

        objects_yaml = object_config.get("objects", {})
        objects = {}

        for object_name, cfg in objects_yaml.items():
            if not cfg.get("enabled", True):
                continue

            input_polygon = cfg.get(
                "input_polygon",
                self.default_input_polygon_for_object(object_name),
            )
            if input_polygon == "":
                self.get_logger().warning(
                    f"Skipping {object_name}: input_polygon is empty"
                )
                continue

            class_name = str(cfg.get("class_name", object_name))
            class_id = int(cfg.get("class_id", -1))

            objects[object_name] = {
                "class_name": class_name,
                "class_id": class_id,
                "confidence_threshold": float(
                    cfg.get(
                        "confidence_threshold",
                        self.default_confidence_threshold,
                    )
                ),
                "input_polygon": self.resolve_topic(input_polygon),
            }

        if len(objects) == 0:
            raise RuntimeError(
                f"No enabled objects with valid input_polygon found in {object_config_file}"
            )

        return objects

    @property
    def yolo_is_fresh(self):
        if self.last_yolo_msg_time is None:
            return False

        age = (
            self.get_clock().now().nanoseconds
            - self.last_yolo_msg_time.nanoseconds
        ) * 1e-9

        return age < self.yolo_msg_timeout

    def publish_cam_processor_happy(self):
        msg = Bool()
        msg.data = self.detector_enabled and self.yolo_is_fresh
        self.cam_processor_happy_pub.publish(msg)

    def detections_cb(self, msg: DetectionArray):
        self.last_yolo_msg_time = self.get_clock().now()

        if not self.detector_enabled:
            return

        best_by_object = {
            object_name: {
                "det": None,
                "score": -1.0,
            }
            for object_name in self.objects.keys()
        }

        for det in msg.detections:
            for object_name, cfg in self.objects.items():
                if not self.matches_detection(det, cfg):
                    continue

                score = float(det.score)

                if score < cfg["confidence_threshold"]:
                    continue

                w = float(det.bbox.size.x)
                h = float(det.bbox.size.y)

                if w <= 0.0 or h <= 0.0:
                    continue

                if score > best_by_object[object_name]["score"]:
                    best_by_object[object_name]["score"] = score
                    best_by_object[object_name]["det"] = det

        stamp = msg.header.stamp
        if stamp.sec == 0 and stamp.nanosec == 0:
            stamp = self.get_clock().now().to_msg()

        for object_name, best in best_by_object.items():
            det = best["det"]

            if det is None:
                continue

            poly = self.detection_to_polygon(det, stamp)
            self.object_publishers[object_name].publish(poly)

    @staticmethod
    def matches_detection(det, cfg):
        det_class_name = str(det.class_name)

        if cfg["class_name"] != "" and det_class_name == cfg["class_name"]:
            return True

        if cfg["class_id"] >= 0 and int(det.class_id) == cfg["class_id"]:
            return True

        return False

    def detection_to_polygon(self, det, stamp):
        cx = float(det.bbox.center.position.x)
        cy = float(det.bbox.center.position.y)
        theta = float(det.bbox.center.theta)
        w = float(det.bbox.size.x)
        h = float(det.bbox.size.y)

        corners = self.obb_to_corners(cx, cy, w, h, theta)

        msg = PolygonStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = self.camera_frame

        for px, py in corners:
            x_norm, y_norm = self.pixel_to_normalized(px, py)

            p = Point32()
            p.x = x_norm
            p.y = y_norm
            p.z = 0.0
            msg.polygon.points.append(p)

        return msg

    def pixel_to_normalized(self, px, py):
        x_norm = ((px - self.image_width / 2.0) / (self.image_width / 2.0))
        y_norm = ((py - self.image_height / 2.0) / (self.image_height / 2.0))

        return float(x_norm), float(y_norm)

    @staticmethod
    def obb_to_corners(cx, cy, w, h, theta):
        local = [
            (-w / 2.0, -h / 2.0),
            (w / 2.0, -h / 2.0),
            (w / 2.0, h / 2.0),
            (-w / 2.0, h / 2.0),
        ]

        c = math.cos(theta)
        s = math.sin(theta)

        corners = []

        for x, y in local:
            px = cx + x * c - y * s
            py = cy + x * s + y * c
            corners.append((px, py))

        return corners          

    def handle_enable_detector(self, request, response):
        self.detector_enabled = True
        response.success = True
        response.message = "YOLO estimator adapter enabled"
        self.get_logger().info(response.message)
        return response

    def handle_disable_detector(self, request, response):
        self.detector_enabled = False
        response.success = True
        response.message = "YOLO estimator adapter disabled"
        self.get_logger().info(response.message)
        return response


def main():
    rclpy.init()
    node = YoloEstimatorAdapter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()