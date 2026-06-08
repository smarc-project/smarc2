# Simulation
This directory contains the SMaRC simulation environment submodules.
- These are not ROS packages.
- **These are [submodules](../documentation/Working%20with%20submodules.md).**
- They can be cloned and used independently of the rest of the smarc2 repository.

# Installation
Follow this: https://github.com/smarc-project/SMARCAssets/blob/master/README.md

**Documentation of the simulation components, methods, vehicles, systems etc. are inside the Assets submodule where the code for most of it lives.**

### The packages
**SmarcAssets**: Common package that contains all the sensors, prefabs, vehicles, etc.
Should be imported from the package manager in Unity if used in a different project. This is where MOST of the useful things are.

**SmarcUnity**: Uses the High Def. Render Pipeline to produce some good looking water and realistic waves. 
Runs fast enough for realtime usage while looking pretty. Requires a decent GPU to run smoothly.


## Running on Macs with VM/Docker or Windows with WSL
> Intel-based macs should just use a VM of Ubuntu 22.04 if ROS is desired, otherwise all packages can be run within MacOS and the following part can be ignored.

Apple silicon macs can do the following to get the sim + ros working.
This is due to a lack of apple-silicon-compiled Ubuntu version of Unity (you can see how that is a horrible combination).

Do these to get stuff running:
- Either [use docker](../docker/README.md) or a VM to get Ubunbtu 22.04 and all the ROS stuff.
  - This part will work fine because you will be compiling things on the apple silicon.
  - If you followed the docker example, the sim in docker WONT run. Because the binaries are for x86 systems and you are on apple.
- Install Unity Hub on mac/win.
  - Get personal license.
  - No need to install an editor at this point.
 

## Advanced use

### Running headless

In general, this will run the sim in the command line:
`./<name_of_exec> -nographics -batchmode`

If you are running in docker(with [our image](../docker/README.md)), this works just as well.
The executables should be availble in this directory already.
You could either run the sim directly with build/exec or run bash and run it yourself manually.

Since this runs wihtout graphics, the only practical way to interact with the sim is over ROS.
To do so, run the [unity bridge node](../scripts/unity_ros_bridge.sh) in the same container/machine and check the topics as you would normally (probably in a third terminal).

### End to end docker example

See [the docker readme!](../docker/README.md)

- Clone **the project** and **assets** as described above
  - Open **the project**.
  - Robotics -> ROS Settings
    - Change ROS IP and Port to whatever your docker/VM is using.
- You should now be able to follow the other readmes. Don't forget to change the ROS IP in `unity_ros2_bridge.sh` accordingly.
