# Submodules
We use some git submodules in this repo.
Here you can read why that is the case and how you can use them.

## Why?
Because some packages are optional under different setups.


Examples:
- You are developing a control algorithm, on Ubuntu 22.04 on your desktop, for long-distance missions with algae.
  - You want to test this algorihm.
  - To do so, you need to run it on simulation.
    - So you pull the simulation submodules.
    - These submodules can be kind of large and require a graphical interface.
      - Meaning they are useless on the real robot, and thus should not be pulled in there.
---

Or the other way around:

- You are developing a driver for a sonar system.
  - This is a driver, meaning it only makes sense when the hardware is present.
  - The hardware can not be connected to a desktop computer.
    - Thus this driver package should not be pulled on one.
    - It can be pulled on the real robot that has the hardware.

---
## How?

### Easy way...
Just use [the script provided here](../scripts/get-submodules.sh) to quickly get/update submodules that matter to you with one command.


### ...or the "hard" way
Assuming you have already cloned this repository. You can see all the submodules under `.gitmodules` file at the root of this repo. You can also just modify that file for all add/remove/update operatons. You can also specify specific branch that should be used for a repo here by adding `branch=...`. Otherwise the default master branch will be used. Also remember that once pulled, these are simple git repos, and all the normal git operations work as they should.

**All code here should be run in the `smarc2` folder. If you see `.gitmodules` when you `ls`, you good.**

Run `git submodule sync` if you change things in `.gitmodules` manually.


### Check your submodules
```bash
git submodule status
```
will show a list of submodules on your local device with their HEAD, could look like this:
```
-6d1a439dce9fbad14ffa779abf633acb4d3b5e02 external_packages/ROS-TCP-Endpoint
 37433070bb7a6232eed84b586813939dffce7519 external_packages/mqtt_bridge (0.1.0-73-g3743307)
 64bb5999e5cf15cfa4ff67ca24321d46460a1369 simulation/SMARCUnityAssets (heads/master)
 c7f9cafdfa4bf4dfc59c6fd111abf9f4855aaf49 simulation/SMARCUnityHDRP (heads/master)
 af22c7bbc08baad040c56e09b4051e9aae664004 simulation/SMARCUnityStandard (heads/master)
```
Notice the `-` and lack of tag on the first line. This indicates that I do not have this submodule on my disk, but it is defined for this repository.

### Acquire a(ll) submodule(s)
Get all the submodules in this repo:
```bash
git submodule update
```
Get a specific submodule:
```bash
git submodule update <path to folder>
```
The path to the folder should be the exact same as the one mentioned in the `.gitmodules` file.
Example:
```bash
cd colcon_ws/smarc2
ls
> ... .gitmodules
git submodule update external_packages/ROS-TCP-Endpoint
```

### Update submodules from their remote
This will basically do a `git pull` in every submodule. 
It will pull it if it is not there.
You can also pass it a path to udpate a specific submodule.
```bash
git submodule update --remote
```

### Add a new submodule
```bash
git submodule add <remote link to repo> <path to repo>
```
Or just modify `.gitmodules` directly.

Example:
```bash
git submodule add https://github.com/KKalem/ROS-TCP-Endpoint external_packages/ROS-TCP-Endpoint
```


