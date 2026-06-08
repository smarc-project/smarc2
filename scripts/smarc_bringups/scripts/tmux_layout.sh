#!/usr/bin/env bash

tmux_make_layout() {
  local target_session="$1"
  local window_name="$2"
  local layout="$3"

  if [[ -z "$target_session" || -z "$window_name" || -z "$layout" ]]; then
    echo "usage: tmux_make_layout <session> <window-name> '<layout>'" >&2
    echo "example: tmux_make_layout mysession Drivers 'row(var(CMD1), 2:var(CMD2), pane)'" >&2
    return 1
  fi

  if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux not found in PATH" >&2
    return 1
  fi

  if ! tmux has-session -t "$target_session" 2>/dev/null; then
    echo "tmux session '$target_session' does not exist" >&2
    return 1
  fi

  _tml_trim() {
    local s="$1"
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    printf '%s\n' "$s"
  }

  _tml_kind() {
    local s
    s="$(_tml_trim "$1")"

    if [[ "$s" =~ ^row\(.*\)$ ]]; then
      printf 'row\n'
    elif [[ "$s" =~ ^col\(.*\)$ ]]; then
      printf 'col\n'
    else
      printf 'leaf\n'
    fi
  }

  _tml_inner() {
    local s
    s="$(_tml_trim "$1")"
    s="${s#*\(}"
    s="${s%)}"
    printf '%s\n' "$s"
  }

  _tml_split_top_level() {
    local s="$1"
    local depth=0
    local token=""
    local c prev=""
    local in_sq=0
    local in_dq=0
    local i
    local delim=$'\037'

    for ((i=0; i<${#s}; i++)); do
      c="${s:i:1}"

      if [[ "$c" == "'" && "$in_dq" -eq 0 && "$prev" != "\\" ]]; then
        ((in_sq = 1 - in_sq))
        token+="$c"
      elif [[ "$c" == '"' && "$in_sq" -eq 0 && "$prev" != "\\" ]]; then
        ((in_dq = 1 - in_dq))
        token+="$c"
      elif [[ "$in_sq" -eq 0 && "$in_dq" -eq 0 ]]; then
        case "$c" in
          '(')
            ((depth++))
            token+="$c"
            ;;
          ')')
            ((depth--))
            token+="$c"
            ;;
          ',')
            if (( depth == 0 )); then
              printf '%s%s' "$token" "$delim"
              token=""
            else
              token+="$c"
            fi
            ;;
          *)
            token+="$c"
            ;;
        esac
      else
        token+="$c"
      fi

      prev="$c"
    done

    [[ -n "$token" ]] && printf '%s' "$token"
  }

  _tml_split_weight_spec() {
    local s="$1"
    local depth=0
    local c prev=""
    local in_sq=0
    local in_dq=0
    local i

    for ((i=0; i<${#s}; i++)); do
      c="${s:i:1}"

      if [[ "$c" == "'" && "$in_dq" -eq 0 && "$prev" != "\\" ]]; then
        ((in_sq = 1 - in_sq))
      elif [[ "$c" == '"' && "$in_sq" -eq 0 && "$prev" != "\\" ]]; then
        ((in_dq = 1 - in_dq))
      elif [[ "$in_sq" -eq 0 && "$in_dq" -eq 0 ]]; then
        case "$c" in
          '(') ((depth++)) ;;
          ')') ((depth--)) ;;
          ':')
            if (( depth == 0 )); then
              printf '%s|%s\n' "${s:0:i}" "${s:i+1}"
              return 0
            fi
            ;;
        esac
      fi

      prev="$c"
    done

    printf '1|%s\n' "$s"
  }

  _tml_unquote_literal() {
    local s
    s="$(_tml_trim "$1")"

    if [[ "$s" =~ ^\".*\"$ ]]; then
      s="${s:1:${#s}-2}"
      s="${s//\\\"/\"}"
      s="${s//\\\\/\\}"
      printf '%s\n' "$s"
      return 0
    fi

    if [[ "$s" =~ ^\'.*\'$ ]]; then
      s="${s:1:${#s}-2}"
      printf '%s\n' "$s"
      return 0
    fi

    printf '%s\n' "$s"
  }

  _tml_resolve_leaf_command() {
    local spec
    spec="$(_tml_trim "$1")"

    if [[ "$spec" == "pane" || "$spec" == "." || "$spec" == "leaf" ]]; then
      return 0
    fi

    if [[ "$spec" =~ ^var\(([A-Za-z_][A-Za-z0-9_]*)\)$ ]]; then
      local var_name="${BASH_REMATCH[1]}"
      if [[ -z "${!var_name+x}" ]]; then
        echo "variable '$var_name' is not set" >&2
        return 1
      fi
      printf '%s\n' "${!var_name}"
      return 0
    fi

    _tml_unquote_literal "$spec"
  }

  _tml_send_command() {
    local target="$1"
    local raw="$2"
    local cmd

    cmd="$(_tml_resolve_leaf_command "$raw")" || return 1
    [[ -z "$cmd" ]] && return 0

    tmux send-keys -t "$target" -- "$cmd" C-m
  }

  _tml_realize() {
    local spec="$1"
    local target="$2"

    spec="$(_tml_trim "$spec")"

    local kind
    kind="$(_tml_kind "$spec")"

    if [[ "$kind" == "leaf" ]]; then
      _tml_send_command "$target" "$spec"
      return $?
    fi

    local inner
    inner="$(_tml_inner "$spec")"

    local children=()
    local item
    local split_output
    local delim=$'\037'

    split_output="$(_tml_split_top_level "$inner")"

    while IFS= read -r -d "$delim" item; do
      item="$(_tml_trim "$item")"
      [[ -n "$item" ]] && children+=("$item")
    done < <(printf '%s%s' "$split_output" "$delim")

    if (( ${#children[@]} == 0 )); then
      echo "empty container: $spec" >&2
      return 1
    fi

    local weights=()
    local specs=()
    local pair w sub
    local total=0

    for item in "${children[@]}"; do
      pair="$(_tml_split_weight_spec "$item")"
      w="${pair%%|*}"
      sub="${pair#*|}"

      w="$(_tml_trim "$w")"
      sub="$(_tml_trim "$sub")"
      w="${w%\%}"

      if ! [[ "$w" =~ ^[0-9]+$ ]] || (( w <= 0 )); then
        echo "invalid weight '$w' in '$item'" >&2
        return 1
      fi

      weights+=("$w")
      specs+=("$sub")
      ((total += w))
    done

    local split_flag
    if [[ "$kind" == "row" ]]; then
      split_flag="-h"
    else
      split_flag="-v"
    fi

    local remaining="$total"
    local i pct newpane

    for ((i=0; i<${#specs[@]}-1; i++)); do
      pct=$(( weights[i] * 100 / remaining ))
      (( pct < 1 )) && pct=1
      (( pct > 99 )) && pct=99

      newpane="$(tmux split-window "$split_flag" -b -P -F '#{pane_id}' -t "$target" -l "${pct}%")" || return 1
      _tml_realize "${specs[i]}" "$newpane" || return 1
      ((remaining -= weights[i]))
    done

    _tml_realize "${specs[-1]}" "$target" || return 1
  }

  local root_pane
  root_pane="$(tmux new-window -P -F '#{pane_id}' -t "$target_session" -n "$window_name")" || return 1
  _tml_realize "$layout" "$root_pane"
}