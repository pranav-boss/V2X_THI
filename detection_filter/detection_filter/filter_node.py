import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray

class DetectionFilterNode(Node):
    def __init__(self):
        super().__init__('detection_filter_node')
        
        # Subscriber to the raw detections topic
        self.subscription = self.create_subscription(
            Detection2DArray,
            'fused/detections',
            self.listener_callback,
            10)
        
        # Publisher for the filtered detections
        self.publisher_ = self.create_publisher(
            Detection2DArray,
            'filtered/fused/detections',
            10)
            
        self.get_logger().info('Detection Filter Node has been started.')

    def listener_callback(self, msg):
        filtered_msg = Detection2DArray()
        # Preserve the original message header
        filtered_msg.header = msg.header
        
        # Iterate over detections to filter out "bed"
        for detection in msg.detections:
            is_valid = True
            
            # Check the results array for the class label
            for result in detection.results:
                # Based on standard ROS 2 vision_msgs/Detection2D
                # result is an ObjectHypothesisWithPose, which contains hypothesis or id/score
                # Handling variations in vision_msgs depending on ROS 2 distro:
                class_label = ""
                if hasattr(result, 'hypothesis'):
                    if hasattr(result.hypothesis, 'class_id'):
                        class_label = str(result.hypothesis.class_id)
                elif hasattr(result, 'id'):
                    class_label = str(result.id)
                elif hasattr(result, 'class_id'):
                    class_label = str(result.class_id)
                
                if 'bed' in class_label.lower():
                    is_valid = False
                    break
            
            if is_valid:
                filtered_msg.detections.append(detection)
                
        self.publisher_.publish(filtered_msg)
        self.get_logger().debug(f'Published {len(filtered_msg.detections)} filtered detections.')

def main(args=None):
    rclpy.init(args=args)
    
    node = DetectionFilterNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # Shutdown if context is still ok
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
