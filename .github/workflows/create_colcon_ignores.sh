#!/usr/bin/env bash
set -euo pipefail

if (( $# == 0 )); then
    echo "Usage: $0 STRING [STRING ...]" >&2
    exit 1
fi

find . -type d -print0 |
while IFS= read -r -d '' dir; do
    # Remove leading "./" for cleaner path handling.
    path="${dir#./}"

    for s in "$@"; do
        # Does this directory path contain the requested string?
        if [[ "$path" == *"$s"* ]]; then
            # Do not create COLCON_IGNORE if a parent directory already
            # matched and therefore already contains one.
            parent="$dir"
            skip=false

            while [[ "$parent" != "." && "$parent" != "/" ]]; do
                parent="$(dirname "$parent")"

                if [[ -e "$parent/COLCON_IGNORE" ]]; then
                    skip=true
                    break
                fi
            done

            if ! $skip; then
                touch "$dir/COLCON_IGNORE"
                printf 'Created %s/COLCON_IGNORE\n' "$path"
            fi

            # No need to test other strings for this directory.
            break
        fi
    done
done