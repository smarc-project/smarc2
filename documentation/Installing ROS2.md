# Installing ROS2


## Step 0: Install ROS-Humble
We use ROS Humble, since it is the current LTS version.
This requires Ubuntu 22.04 at least.

### [Start with the official install guide here](https://docs.ros.org/en/humble/Installation.html)

`ros-humble-desktop-full` should be good for most.

Like with ROS1, setup a workspace. Usually `colcon_ws`.
Notice that ROS2 moved from catkin to colcon for its build process, and there are some minor differences from a user standpoint.

#### One-stop-shop
Coped from the official instructions above, for ubuntu 22.04, installing ROS2 from scratch:

```bash
sudo apt update && sudo apt upgrade

sudo apt install software-properties-common

sudo add-apt-repository universe

sudo apt install curl -y

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update && sudo apt upgrade

sudo apt install ros-humble-desktop

sudo apt install ros-dev-tools
```




### Optional Step 0.5: Tame colcon
Colcon, unlike catkin, cares about your current directory when building, by default.
This is a dumb default.
Put in `~/.colcon/defaults.yaml` the following, **with paths changed to fit your setup**:


```yaml
"": # applies to all colcon subcommands
    log-base: /code/ros2_ws/log

build:
    symlink-install: true
    build-base: /code/ros2_ws/build
    install-base: /code/ros2_ws/install
    base-paths:
        - /code/ros2_ws/src

test:
    build-base: /code/ros2_ws/build
    install-base: /code/ros2_ws/install
    event-handlers:
        - console_direct+
    base-paths:
        - /code/ros2_ws/src
```

Now you can run `colcon build` and `colcon test` from anywhere in your system and it will create its files in the same place, all the time.
You might need to change this if you ever need multiple workspaces and don't want to delete the created folders. If you want to go crazy with this, check out [this example](https://gist.github.com/rotu/62cccb11b25398e9d1aa45021376d546).

You can also find this file [here](../docker/defaults.yaml)

## Installing requirements
Do the following steps in order on a clean ubuntu 22.04 system.
Missing a step will likely produce errors.

`cd` commands are given as inexact, do what they _intend_ to do :)

### This repo and some of its submodules
```bash
mkdir -p colcon_ws/src
cd colcon_ws/src
git clone https://github.com/smarc-project/smarc2.git
cd smarc2
git submodule update --init external_packages/mqtt_bridge/
git submodule update --init external_packages/ROS-TCP-Endpoint/
```

It is good to be aware of git submodules and how they work. We make heavy use of them in this repository.


### Colcon, rosdep, pip
```bash
apt update && apt upgrade # Optional but good
apt install python3-colcon-ros python3-rosdep python3-pip apt-utils ros-dev-tools mosquitto
pip install --user setuptools==58.2.0 # Optional. Stops useless warnings when building
rosdep init
rosdep update
```


### Dependencies of this repo
```bash
cd colcon_ws
./src/smarc2/scripts/rosdep_install_from_src.sh
```

### Build
```bash
cd colcon_ws
source /opt/ros/humble/setup.bash # if you havent put this in your .bashrc
colcon build
```

### Add your workspace to bashrc (or equivalent)
```bash
cd colcon_ws
echo "source /home/YOUR_USERNAME/colcon_ws/install/setup.sh" >> ~/.bashrc
```
and/or
```bash
cd colcon_ws
source install/setup.sh
```
In any terminal you want to use ros in.

## Post-install checks
- Check your vehicles bringup script and its readme.
- `pip list installed | grep numpy`
  - If you see numpy >= 2.0 here, uninstall it
  - Install numpy through apt instead
  - TODO: This seems to be required by only the tf_transformations package that we used during our move from ros1 to ros2. We should really migrate to transforms3d instead.


## [Continue with porting](./Porting%20a%20package.md)

## [Continue with a new package](./Making%20a%20new%20package.md)
