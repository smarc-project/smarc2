import rclpy
from rclpy.node import Node
import subprocess
import time
import atexit
import signal

class TmuxAlertNode(Node):
    def __init__(self):
        super().__init__('tmux_alert_node')

        # Register shutdown cleanup
        atexit.register(self.reset_all_tmux_panes)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        self.original_window_names = {}  # Store window_id -> name
        self.save_window_names()

        self.timer = self.create_timer(1.0, self.check_condition)

    def handle_signal(self, signum, frame):
        self.get_logger().info(f"Received signal {signum}, cleaning up...")
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
            self.get_logger().info("Reset all tmux pane colors to default.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to reset tmux panes: {e.stderr}")

        # Reset window names
        for win_id, original_name in self.original_window_names.items():
            subprocess.call(["tmux", "rename-window", "-t", win_id, original_name])
        self.get_logger().info("Restored original tmux window names and pane colors.")

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
            self.get_logger().info("Stored original tmux window names.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to list tmux windows: {e.stderr}")

    def check_condition(self):
        if self.condition_met():
            self.get_logger().info("Condition met! Triggering alerts...")
            self.alert_tmux()
            self.play_sound()

    def condition_met(self):
        # Dummy logic – replace with real condition
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
            self.get_logger().error(f"Failed to get tmux panes: {e.stderr}")

    def rename_all_windows(self, new_name="!!! ALERT !!!"):
        for win_id in self.original_window_names.keys():
            subprocess.call(["tmux", "rename-window", "-t", win_id, new_name])

        ## Simulate blinking by renaming window rapidly

        #pane_colors = [
        #("white", "black"),
        #("black", "white"),
        #]
        #
        #for _ in range(6):  # Blink 3 times
        #    for fg, bg in pane_colors:
        #        subprocess.call([
        #            "tmux", "select-pane", "-P", f"fg={fg},bg={bg}"
        #        ])
        #        time.sleep(0.3)
        #
        ## Optionally reset to default (you can adjust this)
        #subprocess.call(["tmux", "select-pane", "-P", "default"])

    def play_sound(self):
        # Replace with actual sound file
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
    rclpy.init(args=args)
    node = TmuxAlertNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    subprocess.call(["tmux", "select-pane", "-P", "default"])
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
