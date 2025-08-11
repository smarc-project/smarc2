import numpy as np
import matplotlib.pyplot as plt

"""
This relatively simple script can be used to get a vague idea of the behavior of the position controller
used by the dji. This uses a 1 dimensional example, starting at a distance of 10 meters and outputs the
control outputs and positions over time. It assumes that the drone immediately gets up to the target speed
and is at that speed constantly across the time step. Important metrics include the maximum slope of the 
output, overshoot, and time to reach target.

"""


# time_step = float(input("Enter controller timestep: "))
# max_joy = float(input("Enter maximum speed: "))
# k = float(input("Enter controller gain: "))
# r_sigma = float(input("Enter r_sigma (between 0 and 1): "))

time_step = .1
max_joy = .8
k = .5
r_sigma = .9

dist = 10
max_time = dist / max_joy * 2 

times = np.arange(0, max_time, time_step)
pos = [0.0]
outputs = []
prev_output = 0

for time in times:
    output = k * (dist - pos[-1])
    print(dist - pos[-1])
    if(output > max_joy):
        output = max_joy
    elif(output < -max_joy):
        output = -max_joy
    output = (1 - r_sigma) * output + r_sigma * prev_output
    print(output)
    prev_output = output
    outputs.append(output)
    pos.append(pos[-1] + time_step * output)

plt.figure(1)
plt.plot(times, np.array(outputs))
plt.title("Output graph")
plt.xlabel("time (s)")
plt.ylabel("Output (m/s)")

plt.figure(2)
plt.plot(times, np.array(pos[0:-1]))
plt.title("Position graph")
plt.xlabel("time (s)")
plt.ylabel("Position (m)")
plt.show()
