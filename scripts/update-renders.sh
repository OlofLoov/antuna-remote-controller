#!/usr/bin/env bash
# The images in docs/renders show the schematic, the board and the enclosure
# as they are in this commit. A change to any file they are drawn from
# reruns this and commits the result with it.
#
#   scripts/update-renders.sh           # redraw docs/renders
#   scripts/update-renders.sh --check   # fail when a source changed since
#
# sources.sha256 lists the hash of every file the images are drawn from.
# The check compares hashes, not pixels: KiCad's raytracer does not give
# the same bytes on every machine.
set -euo pipefail
cd "$(dirname "$0")/.."

dest=docs/renders
sources() {
  git ls-files -- hardware/pcb/antuna-remote hardware/pcb/lib hardware/enclosure \
    scripts/render.sh scripts/build-mockup.sh |
    while IFS= read -r file; do
      [[ -f "$file" ]] && printf '%s  %s\n' "$(git hash-object "$file")" "$file"
    done
}

if [[ "${1:-}" == "--check" ]]; then
  if ! diff <(sources) "$dest/sources.sha256" >/dev/null 2>&1; then
    echo "docs/renders is older than its sources. Changed files:" >&2
    diff <(sources) "$dest/sources.sha256" 2>/dev/null | sed -n 's/^[<>] [0-9a-f]*  /  /p' | sort -u >&2
    echo "Run scripts/update-renders.sh and commit docs/renders." >&2
    exit 1
  fi
  exit 0
fi

mkdir -p "$dest"
rm -f "$dest"/*.png
scripts/render.sh "$dest"
sources > "$dest/sources.sha256"
