#!/usr/bin/env python3

from typing import Tuple, Union, Dict, List
import traceback
from math import pi

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

import numpy as np
import cv2
import torch
from cv_bridge import CvBridge

from ultralytics import YOLO
from ultralytics.engine.results import OBB, Results

from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped, PolygonStamped, Point32, Polygon
from std_msgs.msg import Bool
from std_srvs.srv import Trigger

from dji_msgs.msg import Topics, Links, LabeledOBBs


class YOLODetector(Node):
    """ROS 2 node for YOLO-based object detection in AUV perception.

    This node subscribes to camera images, runs YOLO inference to detect objects
    such as sam, buoy, and other classes, and publishes detection results including
    positions, oriented bounding boxes, and annotated images for visualization.
    """

    def __init__(self, name='alars_yolo_detector'):
        super().__init__(
            name,
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True
        )

        self.get_params()

        lw_ratio_margin = float(self.model_params['sam.lw_ratio_margin'])
        self.filt_params = {
            "sam_dim": [self.model_params['sam.width'], self.model_params['sam.length']],
            "lw_ratio_lb": self.model_params['sam.length'] / self.model_params['sam.width'] - lw_ratio_margin,
            "lw_ratio_ub": self.model_params['sam.length'] / self.model_params['sam.width'] + lw_ratio_margin,
        }

        self.dircount = []
        self.horizon = 10

        self.class_names = list(self.model_params["classes.names"])
        self.class_name_to_id = {name: idx for idx, name in enumerate(self.class_names)}
        self.sam_class_id = self.class_name_to_id["sam"]
        self.buoy_class_id = self.class_name_to_id["buoy"]

        self.create_subscription(
            Image,
            self.model_params["topics.raw_image"],
            self.image_callback,
            10
        )

        self.annotated_img_pub = self.create_publisher(
            Image,
            self.model_params["topics.rviz.annotated_image"],
            10
        )
        self.blurred_channel_pub = self.create_publisher(
            Image,
            self.model_params["topics.rviz.bw_blurred_sam"],
            10
        )
        self.head_detection_view_pub = self.create_publisher(
            Image,
            self.model_params["topics.rviz.edges"],
            10
        )

        self.sam_position_pub = self.create_publisher(
            PointStamped,
            self.model_params["topics.predicted_position.sam"],
            10
        )
        self.buoy_position_pub = self.create_publisher(
            PointStamped,
            self.model_params["topics.predicted_position.buoy"],
            10
        )

        self.sam_head_pub = self.create_publisher(
            PolygonStamped,
            self.model_params["topics.predicted_position.sam_head"],
            10
        )
        self.sam_obb_pub = self.create_publisher(
            PolygonStamped,
            self.model_params["topics.predicted_position.sam_obb"],
            10
        )
        self.buoy_obb_pub = self.create_publisher(
            PolygonStamped,
            self.model_params["topics.predicted_position.buoy_obb"],
            10
        )
        self.other_obbs_pub = self.create_publisher(
            LabeledOBBs,
            self.model_params["topics.predicted_position.other_obbs"],
            10
        )

        self.cam_processor_happy_pub = self.create_publisher(
            Bool,
            Topics.CAM_PROCESSOR_HAPPY_TOPIC,
            10
        )
        self.create_timer(
            1.0,
            lambda: self.cam_processor_happy_pub.publish(Bool(data=self.image_is_fresh))
        )

        try:
            self.yolo_model = YOLO(self.model_params['model_path'])
            self.yolo_model.info()
        except Exception as e:
            self.get_logger().warn(
                "\n\nYOLO model import failed; check model_path.\n"
                f"Given path: {self.model_params['model_path']}\n"
            )
            self.get_logger().warn(str(e))
            self.get_logger().warn(traceback.format_exc())

        self.bridge = CvBridge()
        self.detector_enabled = True
        self.image: Image = None

        self.classify_timer = self.create_timer(
            self.model_params['detection.inference_period'],
            self.classify_callback
        )

        self.create_service(
            Trigger,
            Topics.ENABLE_ALARS_DETECTOR_SERVICE_TOPIC,
            self.handle_enable_detector
        )
        self.create_service(
            Trigger,
            Topics.DISABLE_ALARS_DETECTOR_SERVICE_TOPIC,
            self.handle_disable_detector
        )

    @property
    def image_is_fresh(self) -> bool:
        if self.image is None:
            return False
        image_time = self.image.header.stamp.sec + self.image.header.stamp.nanosec * 1e-9
        now = self.get_clock().now()
        now_time = now.to_msg().sec + now.to_msg().nanosec * 1e-9
        return now_time - image_time < 5

    def classify_callback(self):
        if self.image is None or not self.detector_enabled:
            return

        cv_image = self.bridge.imgmsg_to_cv2(self.image, desired_encoding='bgr8')

        results = self.yolo_model.predict(
            source=cv_image,
            conf=self.model_params['detection.confidence_threshold'],
            save=False,
            verbose=False,
            device=self.model_params['device']
        )
        result: Results = results[0]

        filtered_obb, detections = self.filter_detections(result.obb)
        result.obb = filtered_obb

        head = self.identify_head(result.obb, cv_image)

        sam_detections = detections.get("sam", [])
        buoy_detections = detections.get("buoy", [])

        if len(sam_detections) > 0:
            sam_det = sam_detections[0]
            sam_pixels = sam_det["pos"]

            if head is not None:
                self.published_normalized_position(
                    head,
                    (self.image.width, self.image.height),
                    "sam"
                )
                self.publish_normalized_points(
                    head.reshape(1, 2),
                    (self.image.width, self.image.height),
                    "sam_head"
                )

            corners = sam_det["corners"]
            self.publish_normalized_points(
                corners,
                (self.image.width, self.image.height),
                label="sam_obb"
            )
        else:
            sam_pixels = None

        if len(buoy_detections) > 0:
            buoy_det = buoy_detections[0]
            buoy_pixels = buoy_det["pos"]

            self.published_normalized_position(
                buoy_pixels,
                (self.image.width, self.image.height),
                "buoy"
            )

            corners = buoy_det["corners"]
            self.publish_normalized_points(
                corners,
                (self.image.width, self.image.height),
                label="buoy_obb"
            )
        else:
            buoy_pixels = None

        self.publish_other_obbs(detections, (self.image.width, self.image.height))

        im = result.plot()
        if head is not None:
            cv2.circle(
                im,
                center=(int(head[0]), int(head[1])),
                radius=5,
                color=(0, 255, 0),
                thickness=2
            )

        ros_img = self.bridge.cv2_to_imgmsg(im, encoding='bgr8')
        ros_img.header = self.image.header
        self.annotated_img_pub.publish(ros_img)

        self.get_logger().info(
            f"Detections -> sam: {len(sam_detections)}, buoy: {len(buoy_detections)}, head: {head}"
        )

    def get_best_detection_index_for_class(self, obb: OBB, class_id: int):
        cls = obb.cls.cpu().numpy().astype(int)
        conf = obb.conf.cpu().numpy()

        candidate_indices = np.where(cls == class_id)[0]
        if candidate_indices.size == 0:
            return None

        best_local = np.argmax(conf[candidate_indices])
        return int(candidate_indices[best_local])

    def get_detection_indices_for_class(self, obb: OBB, class_id: int) -> List[int]:
        cls = obb.cls.cpu().numpy().astype(int)
        conf = obb.conf.cpu().numpy()

        candidate_indices = np.where(cls == class_id)[0]
        if candidate_indices.size == 0:
            return []

        ordered = candidate_indices[np.argsort(conf[candidate_indices])[::-1]]
        return [int(i) for i in ordered]

    def identify_head(self, result: OBB, im: np.ndarray) -> Union[np.ndarray, None]:
        cls = result.cls.cpu().numpy().astype(int)
        xywhr = result.xywhr
        c4 = result.xyxyxyxy
        head = None
        thresh = 0.8

        sam_indices = np.where(cls == self.sam_class_id)[0]
        if sam_indices.size != 1:
            return None

        sam_index = int(sam_indices[0])

        xywhr_det: torch.Tensor = xywhr[sam_index]
        c4_np: np.ndarray = c4[sam_index].cpu().numpy()
        original_c4 = c4_np.copy()
        length = max(float(xywhr_det[2]), float(xywhr_det[3])) * 0.5

        sliced_im, c4_np = self.slice_image(im, c4_np, thresh, length)

        rgb_sliced_im = cv2.cvtColor(sliced_im, cv2.COLOR_BGR2RGB)
        canny_im, corners_rot = self.rotate_image(
            rgb_sliced_im[:, :, 0],
            c4_np.T,
            (180 / pi) * float(xywhr_det[4])
        )
        canny_im, c4_np = self.slice_image(canny_im, corners_rot.T, thresh, length, 'uneven')

        blur = cv2.GaussianBlur(canny_im, (5, 5), self.model_params["detection.blur_variance"])
        median = np.median(blur)
        lower_threshold = int(max(0, 0.5 * median))
        upper_threshold = int(min(255, 1.5 * median))
        edges = cv2.Canny(blur, threshold1=lower_threshold, threshold2=upper_threshold)

        fdim = {0: np.min, 1: np.max}
        axis = int(float(xywhr_det[2]) < float(xywhr_det[3]))
        coord_min = int(np.min(c4_np, axis=0)[axis])
        coord_max = int(np.max(c4_np, axis=0)[axis])

        if axis == 0:
            sums = (np.sum(edges[:, 0:coord_min]), np.sum(edges[:, coord_max:]))
        else:
            sums = (np.sum(edges[0:coord_min, :]), np.sum(edges[coord_max:, :]))

        argsum = int(np.argmax(np.array(sums)))
        if len(self.dircount) >= self.horizon:
            self.dircount.pop(0)
        self.dircount.append(argsum)

        idx_headc = 0 if np.count_nonzero(np.array(self.dircount) == 0) > len(self.dircount) // 2 else 1

        i = np.nonzero(
            c4_np[:, axis].astype(int) == int(fdim[idx_headc](c4_np, axis=0)[axis])
        )[0]
        head = np.mean(original_c4[i, :], axis=0).astype(int)

        self.head_detection_view_pub.publish(
            self.bridge.cv2_to_imgmsg(edges, encoding='passthrough')
        )
        self.blurred_channel_pub.publish(
            self.bridge.cv2_to_imgmsg(blur, encoding='passthrough')
        )

        return head

    def rotate_image(self, im: np.ndarray, points: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
        assert points.shape[0] == 2, "points array should be shape (2, n)"
        try:
            n = points.shape[1]
        except Exception:
            points = points.reshape(-1, 1)
            n = 1

        w, h = im.shape[1], im.shape[0]
        rotation_matrix = cv2.getRotationMatrix2D(
            center=(w // 2, h // 2),
            angle=angle,
            scale=1.0
        )
        corners_rot = rotation_matrix @ np.concatenate((points, np.ones((1, n))), axis=0)
        canny_im = cv2.warpAffine(im, rotation_matrix, (w, h))

        return canny_im, corners_rot

    def slice_image(
        self,
        im: np.ndarray,
        c4: np.ndarray,
        thresh: float,
        length: float,
        mode: str = 'even'
    ) -> Tuple[np.ndarray, np.ndarray]:
        assert c4.shape == (4, 2), 'shape of corners array is not (4,2)'

        slack = np.ones((1, 4)).flatten() * thresh
        corners = (*np.max(c4, axis=0), *np.min(c4, axis=0))

        if mode != 'even':
            argmax_dim = np.argmax([corners[0] - corners[2], corners[1] - corners[3]])
            slack[[not argmax_dim, (not argmax_dim) + 2]] = thresh / 4

        corners = np.array(corners) + np.array([1, 1, -1, -1]) * float(length) * slack

        f = lambda x, t: min(max(round(x), 0), t)
        corners = np.array(list(map(f, corners, (*im.shape[1::-1], *im.shape[1::-1]))))

        return im[corners[3]:corners[1], corners[2]:corners[0]], c4 - corners[2:]

    def filter_detections(self, obb: OBB):
        cls = obb.cls.cpu().numpy().astype(int)
        conf = obb.conf.cpu().numpy()
        num_dets = cls.size

        detections: Dict[str, List[dict]] = {}
        final_mask = np.zeros(num_dets, dtype=bool)

        multiple_other = bool(self.model_params["detection.multiple_other_detections"])

        for class_id, class_name in enumerate(self.class_names):
            if class_id in [self.sam_class_id, self.buoy_class_id]:
                candidate_indices = self.get_detection_indices_for_class(obb, class_id)[:1]
            else:
                candidate_indices = self.get_detection_indices_for_class(obb, class_id)
                if not multiple_other:
                    candidate_indices = candidate_indices[:1]

            if len(candidate_indices) == 0:
                continue

            for idx in candidate_indices:
                det_conf = float(conf[idx])

                class_threshold = self.model_params["detection.per_class_confidence"].get(
                    class_name,
                    self.model_params["detection.confidence_threshold"]
                )
                if det_conf < class_threshold:
                    continue

                if class_id == self.sam_class_id:
                    w = float(obb.xywhr[idx][2])
                    h = float(obb.xywhr[idx][3])
                    if min(w, h) <= 1e-6:
                        continue
                    lw_ratio = max(w, h) / min(w, h)
                    if not (self.filt_params["lw_ratio_lb"] <= lw_ratio <= self.filt_params["lw_ratio_ub"]):
                        continue

                final_mask[idx] = True
                detections.setdefault(class_name, []).append({
                    "index": idx,
                    "class_id": class_id,
                    "class_name": class_name,
                    "pos": obb.xywhr[idx][0:2].cpu().numpy(),
                    "conf": det_conf,
                    "corners": obb.xyxyxyxy[idx].cpu().numpy(),
                })

        filtered_obb = obb[torch.from_numpy(final_mask)]
        return filtered_obb, detections

    def published_normalized_position(self, p: tuple, wh: tuple, label: str):
        point = PointStamped()
        point.header.stamp = self.get_clock().now().to_msg()
        point.header.frame_id = self.model_params["frames.camera"]
        point.point.x = float((p[0] - wh[0] / 2) / (wh[0] / 2))
        point.point.y = float((p[1] - wh[1] / 2) / (wh[1] / 2))

        if label == 'sam':
            self.sam_position_pub.publish(point)
        elif label == 'buoy':
            self.buoy_position_pub.publish(point)
        else:
            self.get_logger().error('Position not published, label should be "sam" or "buoy"')

    def publish_normalized_points(self, points: np.ndarray, wh: tuple, label=None):
        poly = PolygonStamped()
        poly.header.stamp = self.image.header.stamp
        poly.header.frame_id = self.model_params["frames.camera"]

        w, h = wh
        for px, py in points:
            p = Point32()
            p.x = float((px - w / 2) / (w / 2))
            p.y = float((py - h / 2) / (h / 2))
            poly.polygon.points.append(p)

        if label == "sam_head":
            self.sam_head_pub.publish(poly)
        elif label == "sam_obb":
            self.sam_obb_pub.publish(poly)
        elif label == "buoy_obb":
            self.buoy_obb_pub.publish(poly)
        else:
            self.get_logger().error(f'Label not recognized: {label}')

    def publish_other_obbs(self, detections: Dict[str, List[dict]], wh: tuple):
        msg = LabeledOBBs()
        msg.header.stamp = self.image.header.stamp
        msg.header.frame_id = self.model_params["frames.camera"]

        w, h = wh
        for class_name, det_list in detections.items():
            if class_name in ["sam", "buoy"]:
                continue

            for det in det_list:
                poly = Polygon()
                for px, py in det["corners"]:
                    p = Point32()
                    p.x = float((px - w / 2) / (w / 2))
                    p.y = float((py - h / 2) / (h / 2))
                    poly.points.append(p)

                msg.obbs.append(poly)
                msg.ids.append(class_name)

        if len(msg.obbs) > 0:
            self.other_obbs_pub.publish(msg)

    def handle_enable_detector(self, request, response):
        self.detector_enabled = True
        response.success = True
        response.message = 'detector enabled'
        self.get_logger().info("Detector enabled")
        return response

    def handle_disable_detector(self, request, response):
        self.detector_enabled = False
        response.success = True
        response.message = 'detector disabled'
        self.get_logger().info("Detector disabled")
        return response

    def image_callback(self, msg):
        self.image = msg

    def get_params(self):
        namespace = "/" + str(self.get_parameter("namespace").value).strip("/")

        expected_types = {
            "device": (str, int),
            "model_path": str,

            "detection.inference_period": (float, int),
            "detection.confidence_threshold": (float, int),
            "detection.blur_variance": (float, int),
            "detection.multiple_other_detections": bool,

            "sam.width": (float, int),
            "sam.length": (float, int),
            "sam.lw_ratio_margin": (float, int),

            "classes.names": list,

            "topics.rviz.annotated_image": str,
            "topics.rviz.bw_blurred_sam": str,
            "topics.rviz.edges": str,

            "topics.predicted_position.sam": str,
            "topics.predicted_position.sam_obb": str,
            "topics.predicted_position.sam_head": str,
            "topics.predicted_position.buoy": str,
            "topics.predicted_position.buoy_obb": str,
            "topics.predicted_position.other_obbs": str,
            "topics.raw_image": str,

            "frames.map": str,
            "frames.quadrotor_odom": str,
            "frames.camera": str,
        }

        per_class_conf = self.get_parameter("detection.per_class_confidence").value
        if per_class_conf is None:
            per_class_conf = {}

        frames_topics = {
            "topics.rviz.annotated_image": namespace + "/" + self.get_parameter("topics.rviz.annotated_image").value,
            "topics.rviz.bw_blurred_sam": namespace + "/" + self.get_parameter("topics.rviz.bw_blurred_sam").value,
            "topics.rviz.edges": namespace + "/" + self.get_parameter("topics.rviz.edges").value,

            "topics.predicted_position.sam": namespace + "/" + Topics.ESTIMATED_AUV_TOPIC,
            "topics.predicted_position.sam_obb": namespace + "/" + Topics.ESTIMATED_AUV_OBB_TOPIC,
            "topics.predicted_position.sam_head": namespace + "/" + Topics.ESTIMATED_AUV_HEAD_TOPIC,
            "topics.predicted_position.buoy": namespace + "/" + Topics.ESTIMATED_BUOY_TOPIC,
            "topics.predicted_position.buoy_obb": namespace + "/" + Topics.ESTIMATED_BUOY_OBB_TOPIC,
            "topics.predicted_position.other_obbs": namespace + "/" + Topics.LABELED_OBBS_TOPIC,
            "topics.raw_image": namespace + "/" + Topics.GIMBAL_CAMERA_RAW_TOPIC,

            "frames.map": namespace.removeprefix("/") + "/" + Links.MAP,
            "frames.quadrotor_odom": namespace.removeprefix("/") + "/" + Links.ODOM,
            "frames.camera": namespace.removeprefix("/") + "/" + Links.GIMBAL_OPTICAL_FRAME,
        }

        self.model_params = {
            k: self.get_parameter(k).value if not k.startswith("frames") and not k.startswith("topics")
            else frames_topics[k]
            for k in expected_types
        }
        self.model_params["detection.per_class_confidence"] = per_class_conf
        self.model_params["frame.camera_pixels"] = "camera_pixels_normalized"

        for key, expected in expected_types.items():
            if not isinstance(self.model_params[key], expected):
                raise TypeError(f"{key} should be {expected}, got {type(self.model_params[key]).__name__}")

        class_names = self.model_params["classes.names"]

        self.get_logger().info(
            f"Class mapping: { {name: idx for idx, name in enumerate(class_names)} }"
        )


def main():
    rclpy.init()
    node = YOLODetector()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == '__main__':
    main()