import subprocess
from rclpy.node import Node
from std_msgs.msg import String


class TTS:
    def __init__(self,
                 node: Node,
                 topic: str = "speak",
                 engine : str = "spd-say"):
        
        self._node = node
        self._topic = topic
        self._engine = engine

        self._speak_sub = self._node.create_subscription(
            String, 
            self._topic, 
            self.speak, 
            10
        )

    def speak(self, text: String):
        t = text.data
        if not t:
            self._node.get_logger().warn("Received empty text for TTS.")
            return
        self._node.get_logger().info(f"Speaking: {t}")
        subprocess.run([self._engine, t])

        

def main():
    import rclpy
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()
    node = Node("tts_node")
    tts = TTS(node)

    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        
