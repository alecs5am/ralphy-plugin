#!/bin/sh
# Rebuild plugins/ralphy/ from committed ralphy sources.
#
#   ./sync.sh [ralphy-checkout] [git-ref]
#
# Defaults: ../ralphy and origin/main. Only committed files are read
# (via `git archive`), so uncommitted work in the checkout never leaks in.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
src_repo=${1:-"$here/../ralphy"}
ref=${2:-origin/main}

sha=$(git -C "$src_repo" rev-parse --verify "$ref^{commit}")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$src_repo" archive "$sha" | tar -x -C "$tmp"
python3 -I "$here/build.py" "$tmp" "$sha"
