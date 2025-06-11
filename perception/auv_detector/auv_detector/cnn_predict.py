#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import numpy as np
import cv2
from PIL import Image as PILImage

# ==== CNN Definition (same as in training file) ====
class AnchorPointCNN(nn.Module):
    def __init__(self):
        super(AnchorPointCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 28 * 28, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 4)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# ==== ROS Node ====
class AnchorPointPredictor(Node):
    def __init__(self):
        super().__init__('anchor_point_predictor')
        self.subscription = self.create_subscription(
            Image,
            '/Quadrotor/core/fpcamera/image',
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()
        self.model = AnchorPointCNN()
        self.model.load_state_dict(torch.load('anchor_point_cnn.pth', map_location=torch.device('cpu')))
        self.model.eval()

        self.input_size = (224, 224)
        self.orig_size = (640, 480)
        self.transform = transforms.Compose([
            transforms.Resize(self.input_size),
            transforms.ToTensor()
        ])

    def listener_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            original_image = cv_image.copy()

            # Preprocess for CNN
            pil_image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            input_tensor = self.transform(pil_image).unsqueeze(0)

            # Inference
            with torch.no_grad():
                output = self.model(input_tensor).squeeze().numpy()

            # Rescale to original image size
            x_scale = self.orig_size[0] / self.input_size[0]
            y_scale = self.orig_size[1] / self.input_size[1]
            x1, y1, x2, y2 = output
            x1, y1 = int(x1 * x_scale), int(y1 * y_scale)
            x2, y2 = int(x2 * x_scale), int(y2 * y_scale)

            # Draw predicted points
            cv2.circle(original_image, (x1, y1), 6, (0, 255, 0), -1)  # P1: Green
            cv2.circle(original_image, (x2, y2), 6, (0, 0, 255), -1)  # P2: Red
            cv2.putText(original_image, f"P1", (x1+5, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(original_image, f"P2", (x2+5, y2-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Show image with overlay
            cv2.imshow("Anchor Points Prediction", original_image)
            cv2.waitKey(1)

            self.get_logger().info(f"Predicted Points: ({x1}, {y1}), ({x2}, {y2})")

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

# ==== Main ====
def main(args=None):
    rclpy.init(args=args)
    predictor = AnchorPointPredictor()
    rclpy.spin(predictor)
    predictor.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()