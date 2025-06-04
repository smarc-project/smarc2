# Emergency abort action server for SAM

This package implements an emergency abort action server for SAM. Upon receiving an emergency abort goal request, it sets VBS and RPM to zero, and sets LCG to specified percentage.

To trigger the emergency abort action manually, run the following command:

```bash
# Level 0 - No emergency
# Level 1 - Emergency
ros2 action send_goal /sam/emergency_action smarc_mission_msgs/action/BaseAction "{goal: {data: '{\"level\": 1}'}}"
```