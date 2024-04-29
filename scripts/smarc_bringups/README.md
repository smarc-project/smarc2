# SMaRC Bringups

A pile of launch files and bash scripts.

This package should contain no executables!

The general structure and naming of launchfiles should resemble the folder structure of the `smarc2` repository.

## Scripts
This is where the bringup bash scripts live.
We use `tmux` to create tabs and launch things in, for all the reasons `tmux` is good for.

In general, these bash scripts should take minimal number of arguments, if any.
If a large number of args are needed, maybe use a `config.yaml` filename to pass as an arg instead.


## TMUX Cheatsheet
- `C-x` means "press control and `x`" at the same time. If its `C-X`, then its "Control Shift x".
- `C-b, d` means "Control+B, release everything, d".
- List sessions: `tmux ls`
- Attach to a session: `tmux attach -t <SESSION_NAME>`. Can be shortened to `tmux att -t sam` for example for a session named `sam0_bringup`
- Detach from a session: `C-b, d`
- Change between windows(tabs): `C-b, <NUM>`
- Scroll in a window: `C-b [` and then arrows/pg up etc. `q` to quit scroll mode.
- Kill tmux server (and all the programs running in all sessions): `tmux kill-server`. This is the ultimate "cleanup". Beware of using this on the real robot!

