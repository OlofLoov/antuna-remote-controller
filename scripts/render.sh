#!/usr/bin/env bash
# Render the schematic, the board and the enclosure to PNGs in <outdir>.
# Whatever does not exist yet is skipped: the board appears once
# antuna-remote.kicad_pcb exists, the enclosure once hardware/enclosure/render.py
# does. CI runs this on every commit (.github/workflows/renders.yml).
set -euo pipefail

out="${1:?usage: scripts/render.sh <outdir>}"
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$out"
out="$(cd "$out" && pwd)"
cd "$root"

if command -v kicad-cli >/dev/null; then
  kicad="kicad-cli"
else
  kicad=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
fi

svg_to_png() {
  if command -v rsvg-convert >/dev/null; then
    rsvg-convert --width 2400 --background-color white -o "$2" "$1"
  else
    inkscape "$1" --export-type=png --export-width=2400 \
      --export-background=white --export-background-opacity=1 --export-filename="$2"
  fi
}

project=hardware/pcb/antuna-remote/antuna-remote
rendered=0

if [[ -f "$project.kicad_sch" ]]; then
  tmp="$(mktemp -d)"
  "$kicad" sch export svg -o "$tmp" "$project.kicad_sch" >/dev/null
  for svg in "$tmp"/*.svg; do
    svg_to_png "$svg" "$out/schematic-$(basename "${svg%.svg}").png"
    rendered=$((rendered + 1))
  done
  rm -rf "$tmp"
fi

if [[ -f "$project.kicad_pcb" ]]; then
  # 3D: raytraced with shadows, in the colors of the board's stackup.
  # Parts whose STEP model is missing show as bare pads, so CI fetches the
  # library models first (scripts/fetch-3d-models.sh).
  view() {
    "$kicad" pcb render --quality high --floor --use-board-stackup-colors \
      --width 1600 --height 1000 --background opaque -o "$out/board-$1.png" "${@:2}" \
      "$project.kicad_pcb" >/dev/null
    rendered=$((rendered + 1))
  }
  view top --side top
  view bottom --side bottom
  view iso --rotate '-35,0,30' --perspective --zoom 0.9
  # 2D: copper and silkscreen per side, the view a layout review needs.
  tmp="$(mktemp -d)"
  "$kicad" pcb export svg -l F.Cu,F.Silkscreen,Edge.Cuts --mode-single --fit-page-to-board \
    --exclude-drawing-sheet -o "$tmp/top.svg" "$project.kicad_pcb" >/dev/null
  "$kicad" pcb export svg -l B.Cu,B.Silkscreen,Edge.Cuts --mirror --mode-single --fit-page-to-board \
    --exclude-drawing-sheet -o "$tmp/bottom.svg" "$project.kicad_pcb" >/dev/null
  for side in top bottom; do
    svg_to_png "$tmp/$side.svg" "$out/layout-$side.png"
    rendered=$((rendered + 1))
  done
  rm -rf "$tmp"
fi

if [[ -f hardware/enclosure/render.py ]]; then
  python3 hardware/enclosure/render.py "$out"
  rendered=$((rendered + 1))
fi

echo "rendered $rendered views into $out"
ls "$out"
