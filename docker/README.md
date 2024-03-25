# Docker
We use docker containers to run tests and such. 

> Maybe we can use containers for all the nodes (or groups of them) as well?
> ROS2 is p2p, so we could have "core" in a container, "slam" in one etc. 

## (Optional) Tame docker
Using sudo all the time is annoying, follow [this guide](https://docs.docker.com/engine/install/linux-postinstall/) to make docker commands sudo-d by default, without you needing to type it.
This has security implications that you can read yourself in that link.

## Cheatsheet
**Build image from dockerfile:** `docker build - -t <name>:<tag> < <path/to/dockerfile>`

If you get errors about "IP not found" or similar, most likely docker is using its cache to skip `apt update`. 
Add `--no-cache` to make it build from scratch.

**Check your images:** `docker images`

An image is a _description_ of what will exist in a container when it is run. Basically a "class", doesn't do anything until its instantiated with its constructor.

**Container from image:** `docker run <name>/<tag>`

**Check your containers:** `docker ps`

**Nuke a container:** `docker remove <container_name>`

**Delete stopped containers**: `docker container prune`

**Delete unused images**: `docker image prune`

A container is an instance of an image. It does things, has files and such. There can be many containers from the same image that do not share anything except their initial state.

* To give container a name: add `--name <name>` to `run`
* To share a folder between host and container: `--mount type=bind,source=<folder path on host>,target=<folder path on container>` (you can use `"$pwd"` in the host path part)
* To make container interactive (so that it doesn't just run and quit): add `-it` flag to `run`, or `exec`

**Start a container that was run before:** `docker start <container_name>`

**Attach to a container that is already running:** `docker attach <container_name>`

Examples:
- Create a new container and run bash in it interactively: `docker run -it <container_name> /bin/bash`
- Run bash in a container that is already started: `docker exec -it <container_name> /bin/bash`

### Common problems
- "When I do `docker start`, it quits right away."
  - You did not give the container a command to run when you did `docker run`. This is usually the case when the entrypoint of the image is not a long-running (or interactive) program. If you used the `dockerfile` in this repo, then you should run `bash` at least. See example above.
- "Failed to create symbolic link ... because existing path cannot be removed: Is a directory" when `colcon build`-ing manually inside a container.
  - Avoid doing so.
  - If you have to: just remove the build, install, log folders inside colcon_ws


### End to end example

Note that what we do here is not exactly best practice, since we'll be running multiple things in one container. 
However, this is easier to understand.
Normally, you should run one program per container, and possibly use docker-compose to arrange them, network them etc.

> Notice that the example here uses `build-me-smarc2.sh` which uses linux-y commands!
> This script by default exposes the container network to the host entirely. For most of us, this is fine. If you are concerned about security, do not use this :)


#### Terminal 1
```bash
# get the repo, get in it
git clone <this repo>
cd smarc2
# build an image out of the dockerfile named "smarc2/base"
# the long build command is in a script
./docker/build-me-smarc2.sh
# check out the image
docker images
# make a container out of the image that runs bash interactively by default
docker run -it smarc2/base
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

## Connecting your host ros2 and dockerized ros2
(This assumes you are on a linux system)

The Dockerfile we use sets `ROS_DOMAIN_ID=42` (so the containers do not by default mess with your system) so you need to tell your host system the same:
- `export ROS_DOMAIN_ID=42`  on the host, on each terminal you want connected to the dockerized ros2 setup.
- When building the container, use build-args like so: `docker build - -t smarc2/base --build-arg UID=$(id -u) --build-arg GID=$(id -g) --build-arg USERNAME=$(whoami)  < Dockerfile`. This makes it so that the container has the same user name, id, and group ids, which makes dockerized-ros2 use the same memory as the host user, which means nodes speak using shared memory = fast and 0 config required. [This script](./build-me-smarc2.sh) has this in it for repeated use~.

