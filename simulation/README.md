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

See [the docker readme!](../docker/README.md)

## Running on Macs
> Intel-based macs should just use a VM of Ubuntu 22.04 and be done with it.

Apple silicon macs can do the following to get the sim + ros working.
This is due to a lack of apple-silicon-compiled Ubuntu version of Unity (you can see how that is a horrible combination).

Do these to get stuff running:
- Either [use docker](../docker/README.md) or a VM to get Ubunbtu 22.04 and all the ROS stuff.
  - This part will work fine because you will be compiling things on the apple silicon.
  - If you followed the docker example, the sim in docker WONT run. Because the binaries are for x86 systems and you are on apple.
- Install Unity Hub on mac.
  - Get personal license.
  - No need to install an editor at this point.
- Clone HDRP/Standard
  - Open as project.
    - If Unity complains about not being able to download Assets, that means you don't have ssh-keys set up with github. There will be multiple complaints because of this, click the option that means "don't care, keep going" on each. To fix this:
      - Clone Assets repository.
      - In the Unity editor, Window -> Package Manager.
      - Check SMARCUnityAssets: should have a red exclamation mark.
      - Click the + button, top left -> Add from disk.
      - Locate `package.json` of SMARCUnityAssets, select it.
      - Done
  - Robotics -> ROS Settings
    - Change ROS IP and Port to whatever your docker/VM is using.
    - This part is system-dependent and MIGHT change, good luck.
- You should now be able to follow the other readmes.