#!/usr/bin/env python3

from pathlib import Path

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_types_from_msg, get_typestore

import numpy as np
import matplotlib.pyplot as plt

from rosbag_types import SmarcRosbagTypestore

smarc_types = SmarcRosbagTypestore()
typestore = smarc_types.construct_custom_typestore()

# Path to the directory with the rosbag. Not the rosbag itself
# due to the way ros2 records bags now.
file ='src/smarc2/scripts/rosbag_analyzer/rosbag2_2024_10_15-11_47_37'

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
