import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        # إنشاء Publisher لنشر الصور
        self.publisher_ = self.create_publisher(Image, '/image_raw', 10)
        
        # إعداد مؤقت لالتقاط الصور بمعدل 10 إطارات في الثانية (لتقليل الحمل على النظام)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # تشغيل الكاميرا وتحديد الأبعاد
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.bridge = CvBridge()
        self.get_logger().info("Camera Node has started successfully.")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # تحويل الصورة إلى رسالة ROS 2 ونشرها
            msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            self.publisher_.publish(msg)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()