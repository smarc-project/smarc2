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

#### Build the image 

Skip this if you have already built the image.

```bash
# Create the workspace (skip if you have it)
mkdir -p ~/colcon_ws/src 
cd ~/colcon_ws/src
git clone <this repo>
cd ~/colcon_ws

# build an image out of the dockerfile named "smarc2/base"
# make sure that you are in the root of the ros workspace to have everything run properly
# notice the . at the end!
# this process will take 6-10min so get a cup of coffee
docker build -t smarc2/base -f src/smarc2/docker/Dockerfile .

# check that the image is there
docker images
```

#### Run the container

The typical practice is that the container be destroyed when it exits. However, for ease of development, we will keep it running even after we exit it, so that if you have to install some package or something, you don't have to do it every time you start the container.

```bash
# Start the container
. src/smarc2/docker/run_container.sh

# you can Ctrl-D to exit the container
# Do not close this terminal if you want to use the container!
```


#### Attach to the container in VSCode

Install `Dev Containers` extension in VSCode.

Press `Ctrl+Shift+P` and type `Dev Containers: Attach to Running Container...` and attach to the container that pops up. This will bring you to the container where you can do all the development.

All the code changes made here will be saved locally as well.

Open a terminal in the container and run ros_tcp_endpoint:
```bash
ros2 launch ros_tcp_endpoint endpoint.launch.py
```

## Connecting your host ros2 and dockerized ros2
(This assumes you are on a linux system)

The Dockerfile we use sets `ROS_DOMAIN_ID=42` (so the containers do not by default mess with your system) so you need to tell your host system the same:
- `export ROS_DOMAIN_ID=42`  on the host, on each terminal you want connected to the dockerized ros2 setup.

