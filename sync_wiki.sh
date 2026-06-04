#!/usr/bin/env bash
set -euo pipefail

############################################
# CONFIG
############################################



DOC_ROOT="${DOC_ROOT:-.}"
SPACE_ID="${FEISHU_WIKI_SPACE_ID:-}"
ROOT_NODE="${FEISHU_WIKI_NODE_TOKEN:-}"

CACHE_FILE=".feishu_sync_cache.json"
IGNORE_FILE=".feishuignore"

[[ -z "$SPACE_ID" ]] && {
  echo "❌ FEISHU_WIKI_SPACE_ID required"
  exit 1
}

[[ -f "$CACHE_FILE" ]] || echo "{}" > "$CACHE_FILE"

############################################
# CACHE
############################################

cache_get() {
  jq -r --arg k "$1" '.[$k] // empty' "$CACHE_FILE"
}

cache_set() {
  local k="$1"
  local v="$2"
  local tmp
  tmp=$(mktemp)
  jq --arg k "$k" --arg v "$v" '.[$k]=$v' "$CACHE_FILE" > "$tmp"
  mv "$tmp" "$CACHE_FILE"
}

############################################
# .feishuignore
############################################

IGNORE_DIRS=()

load_ignore() {
  IGNORE_DIRS=()

  [[ ! -f "$IGNORE_FILE" ]] && return

  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(echo "$line" | xargs)"
    [[ -z "$line" ]] && continue
    IGNORE_DIRS+=("$line")
  done < "$IGNORE_FILE"
}

############################################
# ROOT NODE
############################################

get_root_node() {
  if [[ -n "${ROOT_NODE:-}" ]]; then
    echo "$ROOT_NODE"
    return
  fi

  local node
  node=$(lark-cli wiki +node-list \
    --space-id "$SPACE_ID" \
    --json \
    -q '.data.nodes[] | select(.title=="Docs") | .node_token')

  if [[ -n "$node" ]]; then
    echo "$node"
    return
  fi

  lark-cli wiki +node-create \
    --space-id "$SPACE_ID" \
    --title "Docs" \
    --json \
    -q '.data.node_token'
}

ROOT_NODE="$(get_root_node)"

############################################
# PATH HELP
############################################

rel_path() {
  realpath --relative-to="." "$1"
}

############################################
# NODE CACHE
############################################

declare -A NODE_MEM

get_or_create_node() {
  local path="$1"

  if [[ -n "${NODE_MEM[$path]:-}" ]]; then
    echo "${NODE_MEM[$path]}"
    return
  fi

  local cached
  cached=$(cache_get "node:$path")

  if [[ -n "$cached" ]]; then
    NODE_MEM[$path]="$cached"
    echo "$cached"
    return
  fi

  local parent_token="$ROOT_NODE"

  if [[ "$path" != "." ]]; then
    local parent_path
    parent_path=$(dirname "$path")

    if [[ "$parent_path" != "." ]]; then
      parent_token=$(get_or_create_node "$parent_path")
    fi
  fi

  local title
  title=$(basename "$path")

  echo "📁 node: $path" >&2

  local node_token
  node_token=$(
    lark-cli wiki +node-create \
      --parent-node-token "$parent_token" \
      --title "$title" \
      --json \
      -q '.data.node_token'
  )

  NODE_MEM[$path]="$node_token"
  cache_set "node:$path" "$node_token"

  echo "$node_token"
}

############################################
# FILE SYNC
############################################

handle_md() {
  local file="$1"
  local rel
  rel=$(rel_path "$file")

  local key="file:$rel"
  local file_token
  file_token=$(cache_get "$key")

  echo "📄 sync: $rel"

  if [[ -n "$file_token" ]]; then
    lark-cli markdown +overwrite \
      --file-token "$file_token" \
      --file "$file" \
      --json > /dev/null
    return
  fi

  local dir
  dir=$(dirname "$rel")

  local wiki_token="$ROOT_NODE"

  if [[ "$dir" != "." ]]; then
    wiki_token=$(get_or_create_node "$dir")
  fi

  local out
  out=$(
    lark-cli markdown +create \
      --file "$file" \
      --wiki-token "$wiki_token" \
      --json
  )

  file_token=$(echo "$out" | jq -r '.data.file_token')

  cache_set "$key" "$file_token"
}

############################################
# IGNORE FILTER (NO eval FIX)
############################################

should_ignore() {
  local path="$1"

  for rule in "${IGNORE_DIRS[@]}"; do
    if [[ "$path" == *"$rule"* ]]; then
      return 0
    fi
  done

  return 1
}

############################################
# FILE SCAN (FIXED)
############################################

get_files() {
  while IFS= read -r file; do
    rel_path_file=$(realpath --relative-to="." "$file")

    if should_ignore "$rel_path_file"; then
      continue
    fi

    echo "$file"
  done < <(find "$DOC_ROOT" -type f -name "*.md")
}

############################################
# MAIN
############################################

echo "🚀 Feishu Wiki Sync (v4.1 - fixed)"
echo "SPACE_ID=$SPACE_ID"
echo "ROOT_NODE=$ROOT_NODE"

load_ignore

while IFS= read -r file; do
  handle_md "$file"
done < <(get_files)

echo "✅ Done"