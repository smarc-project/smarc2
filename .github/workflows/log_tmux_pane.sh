#!/usr/bin/env bash
set -eu

pane="$1"
session="$2"
window="$3"
pane_index="$4"

mkdir -p "$GITHUB_WORKSPACE/tmux-logs"

log="$GITHUB_WORKSPACE/tmux-logs/${session}_window-${window}_pane-${pane_index}_${pane#%}.log"

tmux pipe-pane -o -t "$pane" "cat >> '$log'"