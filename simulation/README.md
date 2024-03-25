# Simulation
This directory contains the SMaRC simulation environment submodules.
These might not be ROS packages.
**These should be [submodules](../documentation/Working%20with%20submodules.md)**



## SMARCUnity
The three submodules that start with SMARCUnity are meant to be opened or imported as Unity packages.
Depending on your goals, either the HDRP or the Standard project, with the Assets module on top is used.
Check their individual READMEs for details.

Both the Standard and HDRP versions use the [ROS-TCP-Endpoint](https://github.com/KKalem/ROS-TCP-Endpoint) package to speak to ROS2. 
You can use [this simple script](../scripts/unity_ros_bridge.sh) to run the bridge and then use `rviz2` and `rqt` to check what things look like in ROS.
The ROS connection is especially useful when you are running headless.

You can also acquire the latest released binaries from the releases section of github.

### HDRP
Uses the High Def. Render Pipeline to produce some good looking water and realistic waves. 
Runs fast enough for realtime usage while looking pretty.

### Standard
Uses the "Unity Standard" trading graphical fidelity for _speed_.
If you need to do some reinforcement learning or similar "try a million times" approaches, this is the way to go.

This version can also be very easily ran without graphics. See the following section.

### Assets
Common package that contains all the sensors, prefabs, vehicles, etc.
Should be imported from the package manager in Unity.

## Running headless
> This was only tested with the Standard setup.

In general, this will run the sim in the command line:
`./<name_of_exec> -nographics -batchmode`

If you are running in docker(with [our image](../docker/README.md)), this works just as well.
The executables should be availble in this directory already.
You could either run the sim directly with build/exec or run bash and run it yourself manually.

Since this runs wihtout graphics, the only practical way to interact with the sim is over ROS.
To do so, run the [unity bridge node](../scripts/unity_ros_bridge.sh) in the same container/machine and check the topics as you would normally (probably in a third terminal).

### End to end docker example
Note that what we do here is not exactly best practice, since we'll be running multiple things in one container. 
However, this is easier to understand.
Normally, you should run one program per container, and possibly use docker-compose to arrange them, network them etc.

#### Terminal 1
```bash
# get the repo, get in it
git clone <this repo>
cd smarc2/docker 
# build an image out of the dockerfile named "smarc2/base"
docker build - -t smarc2/base < dockerfile 
# check out the image
docker images
# make a container out of the image that runs bash interactively by default
docker run -it smarc2/base /bin/bash
# you are now inside the container, which by default is in colcon_ws
cd src/smarc2/simulation/binaries/SMaRCUnityStandard
./smarc_unity_standard_linux.x86_64 -nographics -batchmode
# now the sim is running in this terminal
# you can Ctrl-C to kill it
# you can Ctrl-D to detach from it
```

#### Terminal 2
```bash
docker ps
# find the name of the running container
docker exec -it <container_name> /bin/bash
source install/setup.bash
cd src/smarc2/scripts
./unity_ros_bridge.sh
```

#### Terminal 3
```bash
docker exec -it <container_name> /bin/bash
source install/setup.bash
ros2 topic list
# you should see the list of topics from the sim here
```
