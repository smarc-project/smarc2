for file in "$GITHUB_WORKSPACE"/tmux-logs/*; do
    [ -f "$file" ] || continue

    echo "::group::TMUX PANE: $(basename "$file")"
    cat "$file"
    echo "::endgroup::"
done