#!/usr/bin/env bash
# Build the grip mock-up: two printable parts as STEP and STL in
# hardware/enclosure/out/. Key positions come from the board's placement
# file, exported here. Needs uv (`brew install uv`); the Python packages
# are pinned in hardware/enclosure/uv.lock.
set -euo pipefail
cd "$(dirname "$0")/.."
kicad="kicad-cli"
command -v kicad-cli >/dev/null || kicad=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
# The board's drill origin is the shell's top left corner.
"$kicad" pcb export pos --format csv --units mm --use-drill-file-origin --side front \
  -o "$work/placement.csv" hardware/pcb/antuna-remote/antuna-remote.kicad_pcb >/dev/null
out="${1:-hardware/enclosure/out}"
uv run --project hardware/enclosure --frozen python hardware/enclosure/mockup.py "$work/placement.csv" "$out"
if [[ -n "${RENDER_TO:-}" ]]; then
  uv run --project hardware/enclosure --frozen python hardware/enclosure/render.py "$work/placement.csv" "$RENDER_TO"
fi
