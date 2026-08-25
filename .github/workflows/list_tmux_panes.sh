#!/usr/bin/env bash

printf "%-20s %-20s %-6s %s\n" \
    "SESSION" "WINDOW" "PANE" "COMMAND"

tmux list-panes -a \
    -F '#{session_name}|#{window_name}|#{pane_index}|#{pane_current_command}' |
while IFS='|' read -r session window pane cmd; do
    printf "%-20s %-20s %-6s %s\n" \
        "$session" "$window" "$pane" "$cmd"
done