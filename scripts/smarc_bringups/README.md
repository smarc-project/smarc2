# SMaRC Bringups

A pile of launch files and bash scripts.

> Example use: `ros2 run smarc_bringups sam_bringup.sh`

The general structure and naming of launchfiles should resemble the folder structure of the `smarc2` repository.

## Scripts
This is where the bringup bash scripts live.
We use `tmux` to create tabs and launch things in, for all the reasons `tmux` is good for.

In general, these bash scripts should take minimal number of arguments, if any.
If a large number of args are needed, maybe use a `config.yaml` filename to pass as an arg instead.

### sam_bringup.sh

Launches everything related to SAM. Add the following lines to your .bashrc and restart your terminal. 

```bash
export LOCAL_ROBOT_NAME=<your sam name>

# Local MQTT Broker with mosquitto
export LOCAL_MQTT_BROKER_IP=<your local ip>
export LOCAL_MQTT_BROKER_PORT=<your local port>

# WARA-PS MQTT Broker
#export LOCAL_MQTT_BROKER_IP=20.240.40.232·
#export LOCAL_MQTT_BROKER_PORT=1884
```
This allows us to change the bringup as we see fit without having to worry
about individual setups regarding MQTT and the robot name. If you want to use
the WARA-PS MQTT Broker instead, use uncomment the last two lines instead.

In the beginning of the script, you can set whether you're on SAM or not.

### dji_bringup.sh

Launches everything related to DJI drones and the ALARS project.
**You will need the submodule in `messages/psdk_interfaces` to run the captain this bringup launches.**


## TMUX Cheatsheet
- `C-x` means "press control and `x`" at the same time. If its `C-X`, then its "Control Shift x".
- `C-b, d` means "Control+B, release everything, d".
- List sessions: `tmux ls`
- Attach to a session: `tmux attach -t <SESSION_NAME>`. Can be shortened to `tmux att -t sam` for example for a session named `sam0_bringup`
- Detach from a session: `C-b, d`
- Change between windows(tabs): `C-b, <NUM>`
- Scroll in a window: `C-b [` and then arrows/pg up etc. `q` to quit scroll mode.
- Kill tmux server (and all the programs running in all sessions): `tmux kill-server`. This is the ultimate "cleanup". Beware of using this on the real robot!

