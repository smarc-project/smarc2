# Simulation
This directory contains the SMaRC simulation environment submodules.
- These are not ROS packages.
- **These are [submodules](../documentation/Working%20with%20submodules.md).**
- They can be cloned and used independently of the rest of the smarc2 repository.



## SMARCUnity
The three submodules that start with SMARCUnity are meant to be used as Unity projects (HDRP, Standard) or packages (Assets).
Check their individual READMEs for details specific to each.

**Documentation of the simulation components, methods, vehicles, systems etc. are inside the Assets submodule where the code for most of it lives.**

### The packages
**Assets**: Common package that contains all the sensors, prefabs, vehicles, etc.
Should be imported from the package manager in Unity. This is where MOST of the useful things are.

**HDRP**: Uses the High Def. Render Pipeline to produce some good looking water and realistic waves. 
Runs fast enough for realtime usage while looking pretty. Requires a decent GPU to run smoothly.

**Standard**: Uses the "Unity Standard" rendering pipeline, trading graphical fidelity for _speed_.
If you need to do some reinforcement learning or similar "try a million times" approaches, this is the way to go. This version can also be very easily ran without graphics.

### First time installation
- Clone SMARCUnityHDRP and/or SMARCUnityStandard (referred to as "**the project**" going forward) and SMARCUnityAssets (**Assets**) repositories into the the *same folder*.
  - **The project** is configured to access **Assets** as a sibling.
  - If you want to arrange them differently, you will need to modify the `manifest.json` file in `TheProject/Packages` to point to wherever you placed **Assets**.
  - Do not place **Assets** inside **the project**.
- Open Unity Hub
  - Add -> Project from disk.
  - Locate **the project**.
  - If it tells you "you do not have the right editor version" choose "download".
  - It will take a bit of time to compile everything for the first time, let it be.
  - **The project** should now appear in the hub going forward.

> You can also acquire the latest released binaries from the [releases section of github](https://github.com/smarc-project/smarc2/releases). These are usually outdated, but likely more stable. If you encounter bugs here, try a cloned version first.

#### ROS connection
- Both the Standard and HDRP versions use the [ROS-TCP-Endpoint](https://github.com/KKalem/ROS-TCP-Endpoint) package to speak to ROS2. 
  - You can use [this simple script](../scripts/unity_ros_bridge.sh) to run the bridge and then use `rviz2` and `rqt` to check what things look like in ROS.
- The ROS connection is especially useful when you are running headless.




### ROS Messages
These are generated from within the editor:
- Robotics -> Generate ROS Messages...
- Fill in the fields in the pop-up
  - Usually you can not generate these INTO the SMARCUnityAssets package, so place the RosMessages folder anywhere for now
- Cut/Paste the generated RosMessages folder into `SMARCUnityAssets/Runtime/Scripts/VehicleComponents/ROS/Core/RosMessages`

### Running headless
> This was only tested with the Standard setup.

In general, this will run the sim in the command line:
`./<name_of_exec> -nographics -batchmode`

If you are running in docker(with [our image](../docker/README.md)), this works just as well.
The executables should be availble in this directory already.
You could either run the sim directly with build/exec or run bash and run it yourself manually.

Since this runs wihtout graphics, the only practical way to interact with the sim is over ROS.
To do so, run the [unity bridge node](../scripts/unity_ros_bridge.sh) in the same container/machine and check the topics as you would normally (probably in a third terminal).

### End to end docker example

See [the docker readme!](../docker/README.md)

## Running on Macs with ROS
> Intel-based macs should just use a VM of Ubuntu 22.04 if ROS is desired, otherwise all packages can be run within MacOS and the following part can be ignored.

Apple silicon macs can do the following to get the sim + ros working.
This is due to a lack of apple-silicon-compiled Ubuntu version of Unity (you can see how that is a horrible combination).

Do these to get stuff running:
- Either [use docker](../docker/README.md) or a VM to get Ubunbtu 22.04 and all the ROS stuff.
  - This part will work fine because you will be compiling things on the apple silicon.
  - If you followed the docker example, the sim in docker WONT run. Because the binaries are for x86 systems and you are on apple.
- Install Unity Hub on mac.
  - Get personal license.
  - No need to install an editor at this point.
- Clone **the project** and **assets** as described above
  - Open **the project**.
  - Robotics -> ROS Settings
    - Change ROS IP and Port to whatever your docker/VM is using.
- You should now be able to follow the other readmes. Don't forget to change the ROS IP in `unity_ros2_bridge.sh` accordingly.