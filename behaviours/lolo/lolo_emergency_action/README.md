# Emergency abort action server for Lolo

This package implements an emergency abort action server for Lolo. 
Upon receiving an emergency abort goal request, is sends an ABORT!

To trigger the emergency abort action manually, run the following command:

```bash
ros2 topic pub /lolo/abort std_msgs/Empty {}
```
