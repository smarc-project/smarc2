launchfile:
ros2 launch floatsam_move_to floatsam_all.launch.py

send goal:
ros2 action send_goal /floatsam_usv/move_to smarc_msgs/action/BaseAction   "{goal: {data: '{\"latitude\": 58.8394970495000, \"longitude\": 17.650843044440000, \"tolerance\": 1.0, \"speed\": 2.0}'}}"

ros2 action send_goal /floatsam_usv/loiter_heading smarc_msgs/action/BaseAction "{goal: {data: '{\"duration\": 15, \"heading\": 3.14}'}}"