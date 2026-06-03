import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PolygonStamped, Point32
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # 1. الاشتراك في بيانات الكاميرا
        self.subscription = self.create_subscription(
            Image, '/image_raw', self.image_callback, 10)
            
        # 2. إنشاء Publisher لنشر زوايا القطعة كـ مضلع (Polygon)
        self.publisher_ = self.create_publisher(
            PolygonStamped, '/painting_target_corners', 10)
        
        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")
        
        # 3. إعدادات التحويل الهندسي
        pixel_points = np.array([
            [50, 53],   [590, 61], 
            [38, 398],  [579, 415]
        ], dtype=np.float32)

        # أبعاد مساحة العمل الدقيقة بالسنتيمتر
        real_world_points = np.array([
            [0, 0], [10.8, 0], 
            [0, 8.1], [10.8, 8.1]      
        ], dtype=np.float32)

        self.H, _ = cv2.findHomography(pixel_points, real_world_points)
        self.get_logger().info("Vision Node is ready and waiting for frames...")

    def get_real_coords(self, px, py):
        vec = np.array([px, py, 1.0], dtype=np.float32)
        real = np.dot(self.H, vec)
        return real[0] / real[2], real[1] / real[2]

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        results = self.model(frame, conf=0.5, verbose=False)

        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                x1, y1, x2, y2 = map(int, boxes[0].xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                
                # تجهيز رسالة ROS
                poly_msg = PolygonStamped()
                poly_msg.header.stamp = self.get_clock().now().to_msg()
                poly_msg.header.frame_id = "camera_link" 
                
                for px, py in corners:
                    rx, ry = self.get_real_coords(px, py)
                    cv2.circle(frame, (px, py), 4, (0, 0, 255), -1)
                    
                    pt = Point32()
                    pt.x = float(rx)
                    pt.y = float(ry)
                    pt.z = 0.0 # المحور Z سيتم تحديده لاحقاً في عقدة التخطيط (Trajectory Planner)
                    poly_msg.polygon.points.append(pt)
                
                self.publisher_.publish(poly_msg)

        cv2.imshow("Painting Target Detection", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()