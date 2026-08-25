#!/usr/bin/env bash

tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index}' |
while read -r pane; do
    echo "=== $pane ==="
    tmux capture-pane -p -t "$pane" | awk 'NF { line=$0 } END { print line }'
    echo "============="
done