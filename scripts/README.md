# Scripts
A pile of bash or python scripts to make life easier.

List them here with a simple explanation so people know what they are running ;)

### get-submodules.sh
Usage:
```bash
cd colcon_ws/smarc2
./scripts/get-submodules.sh <foldername>
```
where `foldername` is a folder (or its first few characters, like `ext` for `external`).

Example: `./scipts/get-submodules.sh ext` will update all submodules in the folder `smarc2/external`. `./scripts/get-submodules.sh sim` will do the same for `smarc2/simulation`.

### launch_everything.py
Just run from the command line, in `/smarc2`.

This script will discover all launch files present within the `smarc2` repo, launch them one by one and document their nodes and their topics etc. into a json file....

### render_strcuture.py
....which this script will read and produce a markdown file from the json that is human readable.
It will also link the launches and packages to their folders in the repo for easy access.

### topics_msg_scanner.py
Scans all `Topics.msg` files in the repo and produces a nice `.md` out of it. With duplicate detection!
Running and keeping the list up to date will be helpful ;)

### rosdep_install_from_src.sh
A single line to install all the dependencies in the `src` directory that aren't sam- lolo- or smarc- named.

Usage:
```bash
cd colcon_ws
./smarc2/scripts/rosdep_install_from_src.sh
```

### unity_ros_bridge.sh
Runs the Unity ROS-TCP-Endpoint with default args for local use. Run from where-ever.
