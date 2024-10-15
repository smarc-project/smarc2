#!/usr/bin/env python3

from pathlib import Path

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_types_from_msg, get_typestore

import numpy as np
import matplotlib.pyplot as plt

# For custom messages, we have to register the message type. Otherwise
# the reader doesn't know what to do.
def guess_msgtype(path: Path) -> str:
    """Guess message type name from path."""
    name = path.relative_to(path.parents[2]).with_suffix('')
    if 'msg' not in name.parts:
        name = name.parent / 'msg' / name.name
    return str(name)

# Get all default ROS2 message types
typestore = get_typestore(Stores.ROS2_HUMBLE)
add_types = {}

# Directory with the custom message definitions. Assumes the ros WS is in the
# home directory
home = str(Path.home())
message_dir = home + '/ros2_ws/src/smarc2/messages/smarc_control_msgs/msg/'

# All custom message files have to be specified here
for pathstr in [message_dir + 'ControlInput.msg',
                message_dir + 'ControlState.msg', message_dir + 'State.msg']:
    msgpath = Path(pathstr)
    msgdef = msgpath.read_text(encoding='utf-8')
    add_types.update(get_types_from_msg(msgdef, guess_msgtype(msgpath)))

typestore.register(add_types)

# Path to the directory with the rosbag. Not the rosbag itself
# due to the way ros2 records bags now.
file ='./rosbag2_2024_10_15-11_47_37'

states = {}
states["t"] = []
states["x"] = []
states["y"] = []
states["z"] = []

events = {}
events["t"] = []

# Create reader instance and open for reading.
with Reader(file) as reader:
    # Topic and msgtype information is available on .connections list.
    for reader_connection in reader.connections:
        print(reader_connection.topic, reader_connection.msgtype)

    # Iterate over messages.
    for connection, timestamp, rawdata in reader.messages():
        if connection.topic == '/parameter_events':
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            events["t"].append(msg.stamp.sec + 1e-9 * msg.stamp.nanosec)
        if connection.topic == '/sam_auv_v1/ctrl/conv/states':
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            states["x"].append(msg.pose.x)
            states["y"].append(msg.pose.y)
            states["z"].append(msg.pose.z)
            states["t"].append(msg.header.stamp.sec + 1e-9 * msg.header.stamp.nanosec)

    print("Bag read")
    
events["trig"] = np.ones((len(events["t"])))

fig = plt.figure()
fig.suptitle("AUV Pose")
ax_x = plt.subplot(311)
ax_y = plt.subplot(312)
ax_z = plt.subplot(313)

ax_x.plot(states["t"],states["x"], label='x')
ax_x.plot(events["t"], events["trig"], '*', label='trigger')
ax_y.plot(states["t"],states["y"])
ax_z.plot(states["t"],states["z"])
ax_x.set_ylabel("x / m")
ax_y.set_ylabel("y / m")
ax_z.set_ylabel("z / m")
ax_z.set_xlabel("t / s")
ax_x.legend()

fig = plt.figure()
plt.title("AUV Trajectory")
plt.plot(states["x"],states["y"])
plt.plot(states["x"][0], states["y"][0], '*', label='start')
plt.xlabel("x / m")
plt.ylabel("y / m")

plt.show()





