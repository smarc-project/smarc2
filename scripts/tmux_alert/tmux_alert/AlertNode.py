import sys
import rclpy
from rclpy.node import Node

import subprocess
import time
import atexit
import signal

from smarc_msgs.msg import Topics as SMaRCTopics
from sensor_msgs.msg import BatteryState

class TmuxAlertNode():
    def __init__(self, node):
        #super().__init__('tmux_alert_node')

        self._node = node

        self._battery_percentage = None

        self.state_sub = node.create_subscription(msg_type=BatteryState, topic=SMaRCTopics.BATTERY_TOPIC, callback=self._battery_cb, qos_profile=10)



        # Register shutdown cleanup
        atexit.register(self.reset_all_tmux_panes)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        self.original_window_names = {}  # Store window_id -> name
        self.save_window_names()

        self.timer = self._node.create_timer(1.0, self.check_condition)

    def _battery_cb(self, msg):
        self._battery_percentage = msg.percentage


    def handle_signal(self, signum, frame):
        self._node.get_logger().info(f"Received signal {signum}, cleaning up...")
        self.reset_all_tmux_panes()
        rclpy.shutdown()

    def reset_all_tmux_panes(self):
        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_index}.#{pane_index}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            pane_ids = result.stdout.strip().split("\n")
            for pane_id in pane_ids:
                subprocess.call(["tmux", "select-pane", "-t", pane_id, "-P", "default"])
            self._node.get_logger().info("Reset all tmux pane colors to default.")
        except subprocess.CalledProcessError as e:
            self._node.get_logger().error(f"Failed to reset tmux panes: {e.stderr}")

        # Reset window names
        for win_id, original_name in self.original_window_names.items():
            subprocess.call(["tmux", "rename-window", "-t", win_id, original_name])
        self._node.get_logger().info("Restored original tmux window names and pane colors.")

    def save_window_names(self):
        try:
            result = subprocess.run(
                ["tmux", "list-windows", "-a", "-F", "#{session_name}:#{window_index}:#{window_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            for line in result.stdout.strip().split("\n"):
                session_window, name = line.rsplit(":", 1)
                self.original_window_names[session_window] = name
            self._node.get_logger().info("Stored original tmux window names.")
        except subprocess.CalledProcessError as e:
            self._node.get_logger().error(f"Failed to list tmux windows: {e.stderr}")

    def check_condition(self):
        if self.condition_met():
            self._node.get_logger().info("Condition met! Triggering alerts...")
            self.alert_tmux()
            self.play_sound()

    def condition_met(self):
        if self._battery_percentage is None:
            self._node.get_logger().info("No Battery Message yet.")
            return False

        if self._battery_percentage < 75:
            return True

    def alert_tmux(self):
        try:
            # Get list of all pane IDs in the current session
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_index}.#{pane_index}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            pane_ids = result.stdout.strip().split("\n")

            # Define alternating colors
            color_sets = [
                ("white", "black"),
                ("black", "white")
            ]

            for _ in range(6):  # Blink 3 times
                for fg, bg in color_sets:
                    for pane_id in pane_ids:
                        subprocess.call([
                            "tmux", "select-pane", "-t", pane_id, "-P", f"fg={fg},bg={bg}"
                        ])
                    self.rename_all_windows("!!! ALERT !!!")
                    time.sleep(0.25)

            # Reset to default styling after alert
            for pane_id in pane_ids:
                subprocess.call(["tmux", "select-pane", "-t", pane_id, "-P", "default"])

        except subprocess.CalledProcessError as e:
            self._node.get_logger().error(f"Failed to get tmux panes: {e.stderr}")

    def rename_all_windows(self, new_name="!!! ALERT !!!"):
        for win_id in self.original_window_names.keys():
            subprocess.call(["tmux", "rename-window", "-t", win_id, new_name])


    def play_sound(self):
        sound_file = "/home/parallels/ros2_ws/src/smarc2/scripts/tmux_alert/resource/siren-alert-96052.mp3"
        try:
            subprocess.Popen([
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel", "quiet",  # suppress console output
                sound_file
            ])
        except Exception as e:
            self.get_logger().error(f"Failed to play sound: {e}")

def main(args=None):
    rclpy.init(args=sys.argv)
    node = rclpy.create_node("AlertNode")
    alert_node = TmuxAlertNode(node)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    subprocess.call(["tmux", "select-pane", "-P", "default"])
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
