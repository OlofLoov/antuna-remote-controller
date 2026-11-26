#!/usr/bin/env bash
# Copy the KiCad library 3D models the board uses into
# hardware/pcb/lib/models/kicad/, which is committed, so renders need no
# download. Run it after scripts/build-board.sh adds a footprint whose model
# is missing there. The tag matches the KiCad version CI runs.
set -euo pipefail
cd "$(dirname "$0")/.."
tag=10.0.8
dest=hardware/pcb/lib/models/kicad
board=hardware/pcb/antuna-remote/antuna-remote.kicad_pcb
grep -o '(model "[^"]*lib/models/kicad/[^"]*"' "$board" | sed 's|.*lib/models/kicad/||; s|"$||' | sort -u |
  while read -r path; do
    [[ -s "$dest/$path" ]] && continue
    mkdir -p "$dest/$(dirname "$path")"
    curl -fsSL --retry 2 -o "$dest/$path" "https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/$tag/$path"
    echo "added $path"
  done
echo "KiCad models in $dest"
