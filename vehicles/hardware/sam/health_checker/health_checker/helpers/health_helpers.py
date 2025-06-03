
# General
import time
from collections import deque
import importlib

# ROS
import rclpy
from rclpy.node import Node


class TopicRateMonitor:
    def __init__(self, node: Node,
                 topics_dict: dict,
                 timeout_time_sec: float=5.0,
                 window_size: int = 5,
                 report_interval: float = 1.0,
                 verbose: bool = False):
        """
        Will check that the topics are maintained at the desired rate
        Args:
            node: The ROS 2 node using this monitor.
            topics: A dict {topic_name: msg_type}
            window_size: Sliding window size for rate calculation.
            report_interval: Seconds between each rate log per topic.
        """
        #
        self.node = node
        self.topics_dict = topics_dict  # { topic_name: [message_type, desired_rate]}
        self.window_size = window_size
        self.timout_time_sec = timeout_time_sec
        self.report_interval = report_interval

        self.verbose = verbose
        # self.report_timer_rate =  # IGNORE FOR NOW

        self.timers = {}
        self.timestamps = {}
        self.timer_output = {}

        self.ready = False
        self.fault = False

        for topic, msg_info in self.topics_dict.items():
            msg_type, msg_rate = msg_info
            if self.verbose:
                self._log(f"Monitoring '{topic}' at {report_interval}s interval")
            self.timestamps[topic] = deque(maxlen=window_size)
            self.timer_output[topic] = False
            node.create_subscription(msg_type, topic, self._make_callback(topic), 10)
            # TODO - for now ignoring the individual timers
            # self.timers[topic] = node.create_timer(report_interval, self._make_reporter(topic))

        # Timer for checking if topics have been received at least once
        self.report_timer = self.node.create_timer(timer_period_sec=float(self.report_interval),
                                                   callback=self.report_callback)

    def _log(self, message):
        self.node.get_logger().info(message)

    def _make_callback(self, topic_name):
        def subscriber_callback(msg):
            if self.verbose:
                self.node.get_logger().info(f"Subscription callback: {topic_name}")
            self.timestamps[topic_name].append(self.node.get_clock().now().nanoseconds/1e9)
        return subscriber_callback

    def _make_timer(self, topic_name):
        def timer_callback():
            self.node.get_logger().info(f"Timer callback: {topic_name}")
            self.timer_output[topic_name] = True
            self.timestamps[topic_name].append(self.node.get_clock().now().nanoseconds/1e9)
        return timer_callback

    # Use this if it is desired that each topic has a timer
    # For now I will just check at a given rate
    # def _make_reporter(self, topic_name):
    #     def report():
    #         topic_names = self.topics_dict.keys()
    #         for topic_name in topic_names:
    #
    #             times = self.timestamps[topic_name]
    #             if len(times) < 2:
    #                 self.node.get_logger().info(f"[{topic_name}] Waiting for data...")
    #                 return
    #
    #             intervals = [t2 - t1 for t1, t2 in zip(times, list(times)[1:])]
    #             if intervals:
    #                 avg_rate = 1.0 / (sum(intervals) / len(intervals))
    #                 self.node.get_logger().info(f"[{topic_name}] Rate: {avg_rate:.2f} Hz")
    #             else:
    #                 self.node.get_logger().info(f"[{topic_name}] Insufficient data.")
    #     return report

    def report_callback(self):
        self.determine_ready()
        self.determine_fault()

    def determine_ready(self):
        if self.ready:
            return True
        for topic_name in self.topics_dict.keys():
            if len(self.timestamps[topic_name]) == 0:
                return False

        # Set to ready
        self.ready = True
        return True

    def determine_fault(self):
        for topic_name, msg_info in self.topics_dict.items():
            msg_type, msg_rate = msg_info
            times = self.timestamps[topic_name]
            if len(times) < 2:
                if self.verbose:
                    self.node.get_logger().info(f"[{topic_name}] Waiting for data...")
                continue

            intervals = [t2 - t1 for t1, t2 in zip(times, list(times)[1:])]
            if intervals:
                avg_rate = 1.0 / (sum(intervals) / len(intervals))

                if self.verbose:
                    self.node.get_logger().info(f"[{topic_name}] Rate: {avg_rate:.2f} Hz")

                    if avg_rate < msg_rate:
                        self.fault = True
                        return True

        return False


class DynamicSubscriberManager:
    def __init__(self, node, target_topics, desired_values, min_rates, fault_callback):
        """
        Args:
            node: The rclpy node instance.
            target_topics: List of topic names to subscribe to.
            desired_values: Dict of topic -> desired value to check against.
            min_rates: Dict of topic -> minimum expected message rate (Hz).
            fault_callback: Function to call when a fault is detected.
                            Should accept (manager_name, fault_message).
        """
        self.node = node
        self.manager_name = self.__class__.__name__
        self.target_topics = target_topics
        self.desired_values = desired_values
        self.min_rates = min_rates
        self.fault_callback = fault_callback

        self.subscriptions = {}
        self.msg_counters = {topic: 0 for topic in target_topics}
        self.last_check_time = self.node.get_clock().now()

        # Set up timers
        self.node.create_timer(1.0, self.check_and_subscribe)  # every 1 sec
        self.node.create_timer(5.0, self.check_message_rates)  # every 5 sec

    def check_and_subscribe(self):
        topics = dict(self.node.get_topic_names_and_types())

        for topic_name in self.target_topics:
            if topic_name in topics and topic_name not in self.subscriptions:
                type_name = topics[topic_name][0]
                self.add_subscription(topic_name, type_name)
                self.node.get_logger().info(f"✅ Subscribed to {topic_name} [{type_name}]")

    def add_subscription(self, topic_name, type_name):
        pkg, _, msg = type_name.partition('/')
        try:
            module = importlib.import_module(f'{pkg}.msg')
            msg_type = getattr(module, msg)
        except ModuleNotFoundError as e:
            self.node.get_logger().error(
                f"Failed to import module '{pkg}.msg' for topic '{topic_name}': {e}"
            )
            return
        except AttributeError as e:
            self.node.get_logger().error(
                f"Message type '{msg}' not found in '{pkg}.msg' for topic '{topic_name}': {e}"
            )
            return
        except Exception as e:
            self.node.get_logger().error(
                f"Unexpected error during import for topic '{topic_name}': {e}"
            )
            return

        desired_value = self.desired_values.get(topic_name)

        def callback(msg_obj, topic=topic_name, desired=desired_value):
            try:
                self.msg_counters[topic] += 1
                if desired is not None:
                    if not self.check_message_match(msg_obj, desired):
                        self.fault_callback(
                            self.manager_name,
                            f"Message mismatch on {topic}. Got: {msg_obj}, Expected: {desired}"
                        )
            except Exception as e:
                self.node.get_logger().error(
                    f"Error in callback for topic '{topic}': {e}"
                )

        try:
            sub = self.node.create_subscription(msg_type, topic_name, callback, 10)
            self.subscriptions[topic_name] = sub
        except Exception as e:
            self.node.get_logger().error(
                f"Failed to create subscription for topic '{topic_name}': {e}"
            )

    def check_message_match(self, msg, desired):
        """
        Compare the received message with the desired value.
        You can customize this per message type if needed.
        """
        try:
            return str(msg) == str(desired)
        except Exception as e:
            self.node.get_logger().error(
                f"Error comparing message on topic: {e}"
            )
            return False

    def check_message_rates(self):
        now = self.node.get_clock().now()
        elapsed_duration = now - self.last_check_time
        elapsed_sec = elapsed_duration.nanoseconds / 1e9 if elapsed_duration.nanoseconds > 0 else 1e-6
        self.last_check_time = now

        for topic, count in self.msg_counters.items():
            actual_rate = count / elapsed_sec
            min_rate = self.min_rates.get(topic, 0.0)
            self.node.get_logger().info(
                f"[{self.manager_name}] {topic}: {actual_rate:.2f} Hz (min {min_rate:.2f} Hz)"
            )

            if actual_rate < min_rate:
                self.fault_callback(
                    self.manager_name,
                    f"Message rate too low on {topic}: {actual_rate:.2f} Hz < {min_rate:.2f} Hz"
                )

            self.msg_counters[topic] = 0  # Reset counter for next check







