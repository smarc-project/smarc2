for file in "$GITHUB_WORKSPACE"/tmux-logs/*; do
    [ -f "$file" ] || continue

    echo "::group::TMUX PANE: $(basename "$file")"
    tail -n 50 "$file" | sed $'s/\033\\[[0-9;?]*[ -/]*[@-~]//g'
    echo "::endgroup::"
done