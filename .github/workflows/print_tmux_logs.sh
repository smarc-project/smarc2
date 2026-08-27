for file in "$GITHUB_WORKSPACE"/tmux-logs/*; do
    [ -f "$file" ] || continue

    echo "::group::TMUX PANE: $(basename "$file")"
    tail -n 50 "$file"
    echo "::endgroup::"
done