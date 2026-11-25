#!/usr/bin/env bash
# Downloads the STEP models for the parts in hardware/pcb/lib from LCSC's
# EasyEDA library. They stay out of git because their license is not
# stated. Needs Python 3 and network access.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
dest=hardware/pcb/lib/antuna.3dshapes
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
python3 -m venv "$work/venv"
"$work/venv/bin/pip" -q install easyeda2kicad==1.0.1
(cd "$work" && "$work/venv/bin/easyeda2kicad" --3d --lcsc_id C49419243 C20346073 --output "$work/lcsc" >/dev/null)
mkdir -p "$dest"
cp "$work/lcsc.3dshapes/WIRELM-SMD_AN54LQ-15.step" "$dest/Raytac_AN54LQ-15.step"
cp "$work/lcsc.3dshapes/OPTO-SMD_TSOP6238TR.step" "$dest/Vishay_TSMP96000TR.step"
echo "STEP models in $dest"
