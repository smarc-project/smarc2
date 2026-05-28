# SMaRC Bringups

A pile of launch files and bash scripts.

> Example use: `ros2 run smarc_bringups sam_bringup.sh`

The general structure and naming of launchfiles should resemble the folder structure of the `smarc2` repository.

## Scripts
This is where the bringup bash scripts live.
We use `tmux` to create tabs and launch things in, for all the reasons `tmux` is good for.

In general, these bash scripts should take minimal number of arguments, if any.
If a large number of args are needed, maybe use a `config.yaml` filename to pass as an arg instead.

### sam_bringup.sh

Launches everything related to SAM. Add the following lines to your .bashrc and restart your terminal. 

```bash
export LOCAL_ROBOT_NAME=<your sam name>

# Local MQTT Broker with mosquitto
export LOCAL_MQTT_BROKER_IP=<your local ip>
export LOCAL_MQTT_BROKER_PORT=<your local port>

# WARA-PS MQTT Broker
#export LOCAL_MQTT_BROKER_IP=20.240.40.232·
#export LOCAL_MQTT_BROKER_PORT=1884
```
This allows us to change the bringup as we see fit without having to worry
about individual setups regarding MQTT and the robot name. If you want to use
the WARA-PS MQTT Broker instead, use uncomment the last two lines instead.

In the beginning of the script, you can set whether you're on SAM or not.

### dji_bringup.sh

Launches everything related to DJI drones and the ALARS project.

- Required manual setup: (TODO declare dependencies etc.)

  - `apt install ros-humble-rmw-zenoh-cpp`
    - You can skip this if your usecase is confined almost entirely to sim/rosbag use.
    - If you skip it, ignore the follow parts about Zenoh as well!
  - `messages/psdk_interfaces`
  - If you want to run the full vision->motion stack: alars_auv_perception has requirements that need special care, check its readme!
    - If you do not need the vision capabilities, you can skip this on your personal machine.

- Only for Orin:

  - `drivers/nau7802_ros2_driver` (requires `pip3 install cedargrove-nau7802 circup`)
  - `drivers/z1_pro_driver` (requires `apt install geographiclib-tools libgeographic-dev ros-humble-compressed-image-transport gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-base  gstreamer1.0-libav`)
  
- Nice to have:
  - rosboard: (`cd ~/colcon_ws/src && git clone https://github.com/dheera/rosboard`, `pip3 install tornado simplejpeg`, `ros2 run rosboard rosboard_node`)
  - rosshow: (`cd ~/colcon_ws/src && git clone https://github.com/dheera/rosshow`)

#### RMW Zenoh setup
Replace `ROS_DOMAIN_ID` and `$JETSON_IP` etc. with what makes sense for your specific case if you're not ALARS.

##### Jetson side .bashrc

```
export ROS_DOMAIN_ID=1
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
```

To make the Jetson connectable from outside, you need to run the zenoh daemon like: `DISCOVERY_SERVER_CMD="export ZENOH_CONFIG_OVERRIDE='listen/endpoints=[\"tcp/0.0.0.0:7447\"]' && ros2 run rmw_zenoh_cpp rmw_zenohd"`.

**Do NOT** put the export command into anything that runs for every terminal (like bashrc). You want the export to only happen for the zenoh router!


##### User side .bashrc

```
export ROS_DOMAIN_ID=1
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
export ZENOH_CONFIG_OVERRIDE='mode="client";connect/endpoints=["tcp/'"$JETSON_IP"':7447", "tcp/'"$JETSON_IP_WG"':7447"];scouting/multicast/enabled=false'
```


#### Camera calibration
`apt install ros-humble-camera-calibration`
With GUI, follow: https://docs.ros.org/en/kilted/p/camera_calibration/doc/tutorial_mono.html
Copy the values into `perception/alars/auv_state_estimation/config/....yaml`

#### Proper torch installation (Jetpack 6.2.2)

After everything above:

```
python3 -m pip uninstall -y torch torchvision torchaudio
python3 -m pip cache purge
python3 -m pip install torch==2.8.0 torchvision==0.23.0 --index-url=https://pypi.jetson-ai-lab.io/jp6/cu126
```

This will complain about numpy version ultralytics wants, if you removed the pip-installed version like auv_yolo_detector's README mentions. But things seem to run regardless.



#### eport serial2usb udev rules
`udevadm info -a -n /dev/ttyUSB0`

find the serial of the serial2usb adapter, put it in `/etc/udev/rules.d/XXXX.rules`

`SUBSYSTEM=="tty", ATTRS{serial}=="A50285BI", SYMLINK+="eport", OWNER="alars", GROUP="alars", MODE="0660"`

then there'll be `dev/eport` as a device that links to that usb2serial

#### Camera udev rules
Since we have multiple cams, of different kinds, we have udev rules setup in the jetson to give them fixed device symlinks under `ls /dev`:
Example:
```
> lsusb
...
Bus 001 Device 019: ID 2e1a:0003 Insta Insta360 X4
...
```

`> apt install v4l-utils`

```
> v4l2-ctl --list-devices
NVIDIA Tegra Video Input Device (platform:tegra-camrtc-ca):
	/dev/media0

Insta360 X4: Insta360 X4 (usb-3610000.usb-4.4):
	/dev/video0
	/dev/video1
	/dev/media1
```

```
> sudo vim /etc/udev/rules.d/99-insta360.rules

SUBSYSTEM=="video4linux", ATTRS{idVendor}=="2e1a", ATTRS{idProduct}=="0003", ATTR{index}=="0", SYMLINK+="insta360x4"
SUBSYSTEM=="video4linux", ATTRS{idVendor}=="2e1a", ATTRS{idProduct}=="0003", ATTR{index}=="1", SYMLINK+="insta360x4_meta"
SUBSYSTEM=="media", ATTRS{idVendor}=="2e1a", ATTRS{idProduct}=="0003", SYMLINK+="insta360x4_media"
```

The above makes `/dev/insta360x4` point to the video stream of the cam, independently of connection timing/port/other cams etc.


## TMUX Cheatsheet
- `C-x` means "press control and `x`" at the same time. If its `C-X`, then its "Control Shift x".
- `C-b, d` means "Control+B, release everything, d".
- List sessions: `tmux ls`
- Attach to a session: `tmux attach -t <SESSION_NAME>`. Can be shortened to `tmux att -t sam` for example for a session named `sam0_bringup`
- Detach from a session: `C-b, d`
- Change between windows(tabs): `C-b, <NUM>`
- Scroll in a window: `C-b [` and then arrows/pg up etc. `q` to quit scroll mode.
- Kill tmux server (and all the programs running in all sessions): `tmux kill-server`. This is the ultimate "cleanup". Beware of using this on the real robot!

