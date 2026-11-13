#!/usr/bin/env bash
# Merge the changes a range of commits made to the manuscript in this
# repository into a clone of the Overleaf project.
#
# usage: send-manuscript.sh <before> <after> <clone>
#
# Each file the commits changed is merged three ways: what it was before
# them, what it is after them, and what the Overleaf project holds now, which
# the authors may have edited since. An edit to other lines of the file is
# kept. An edit to the same lines is a conflict, which is reported, and the
# script fails once every file has been tried, so that nothing is sent.
set -euo pipefail

before=$1
after=$2
clone=$3
directory=manuscript

scratch=$(mktemp -d)
conflicts=0

while IFS=$'\t' read -r status path; do
  relative=${path#"$directory"/}
  target="$clone/$relative"
  case "$status" in
    D)
      rm -f "$target"
      echo "Removed $relative"
      ;;
    A | M)
      git show "$after:$path" > "$scratch/theirs"
      if [ -f "$target" ]; then
        # a file added on both sides has nothing in common to start from
        if ! git show "$before:$path" > "$scratch/base" 2> /dev/null; then
          : > "$scratch/base"
        fi
        if git merge-file -L Overleaf -L before -L repository \
          "$target" "$scratch/base" "$scratch/theirs"; then
          echo "Merged $relative"
        else
          echo "::error::$relative was edited on the same lines in Overleaf and in the repository."
          conflicts=$((conflicts + 1))
        fi
      else
        mkdir -p "$(dirname "$target")"
        cp "$scratch/theirs" "$target"
        echo "Added $relative"
      fi
      ;;
  esac
done < <(git diff --name-status --no-renames "$before" "$after" -- "$directory")

if [ "$conflicts" -gt 0 ]; then
  echo "::error::$conflicts files conflict, so nothing was sent to Overleaf. Run the manuscript workflow by hand to bring the edits made in Overleaf into a pull request, and settle them there."
  exit 1
fi
