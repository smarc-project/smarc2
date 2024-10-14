# sam_joy_xbox

## Installation

While the Xbox controller works with the ros ```joy``` package out of the box, the ```joy``` package does not support the vibration motors or LED feedback. Therefore, this package uses the [xpadneo](https://github.com/atar-axis/xpadneo) advanced linux driver for the Xbox controller.

> Step for installation are taken from the [xpadneo documentation](https://atar-axis.github.io/xpadneo/) and should be followed for up to date instructions. A summary of the steps are provided below.

Install prerequisites:

```bash
sudo apt-get install dkms linux-headers-`uname -r`
```

Clone and install the xpadneo driver:

```bash
git clone https://github.com/atar-axis/xpadneo
cd xpadneo
sudo ./install.sh
```

Install evdev:

```bash
pip3 install evdev
```

At this point you will need to reboot your computer. After rebooting, connect the Xbox controller and check that it is working by connecting the controller and running the following command:

```bash
cd xpadneo/misc/examples/python_evdev_rumble/
python3 rumble.py
```

If the controller is working, you should feel the vibration motors turn on.

## Launch

After following the installation steps and building the ros package, launch the node using the following command:

```bash
roslaunch sam_joy_xbox joy.launch
```

## Controls 

| Button | Action | Vibration Feedback |
| --- | --- | --- |
| ```Left stick``` | Send RPM commands to motors | - | 
| ```Right stick``` | Send thrust vector commands | - | 
| ```A``` | Toggle teleop enable | ```One short pulse``` - Enabled <br>```Two short pulse``` - Disabled |