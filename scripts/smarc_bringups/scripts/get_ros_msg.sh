#!/usr/bin/env bash

# Usage:
# ros_constants smarc_topics smarc_msgs Topics
# echo "${smarc_topics[POS_LATLON_TOPIC]}"

ros_constants() {
    local dest="$1"
    local package="$2"
    local message="$3"

    declare -gA "$dest"
    local -n result="$dest"

    while IFS=$'\t' read -r key value; do
        result["$key"]="$value"
    done < <(
        python3 - "$package" "$message" <<'PY'
import importlib
import sys

package, message = sys.argv[1:3]

module = importlib.import_module(f"{package}.msg")
msg_type = getattr(module, message)

for name in dir(msg_type):
    if name.isupper():
        value = getattr(msg_type, name)
        print(f"{name}\t{value}")
PY
    )
}