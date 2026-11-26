#!/usr/bin/env bash
# Download the KiCad library 3D models the board uses into .tools/3dmodels,
# for machines without KiCad's 3D library (the kicad/kicad CI image). Point
# KICAD10_3DMODEL_DIR at that folder when rendering. The tag matches the
# KiCad version CI runs.
set -euo pipefail
cd "$(dirname "$0")/.."
tag=10.0.8
dest=.tools/3dmodels
board=hardware/pcb/antuna-remote/antuna-remote.kicad_pcb
mkdir -p "$dest"
# shellcheck disable=SC2016 # a literal ${...} in the board file
grep -o '(model "${KICAD10_3DMODEL_DIR}/[^"]*"' "$board" | sed 's|.*KICAD10_3DMODEL_DIR}/||; s|"$||' | sort -u |
  while read -r path; do
    [[ -s "$dest/$path" ]] && continue
    mkdir -p "$dest/$(dirname "$path")"
    curl -fsSL --retry 2 -o "$dest/$path" "https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/$tag/$path" ||
      echo "missing $path"
  done
echo "KiCad models in $dest"
