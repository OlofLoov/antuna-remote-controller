#!/usr/bin/env bash
# Rebuild hardware/pcb/antuna-remote/antuna-remote.kicad_pcb from the
# schematic and the positions in hardware/pcb/layout/build_board.py. This
# replaces the board, tracks included: run scripts/route-board.sh after it.
set -euo pipefail
cd "$(dirname "$0")/.."
python=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
[[ -x "$python" ]] || python=python3
"$python" hardware/pcb/layout/build_board.py 2> >(grep -v -e Fontconfig -e wxApp >&2)
