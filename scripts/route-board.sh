#!/usr/bin/env bash
# Route the board with Freerouting: export Specctra DSN, autoroute, import
# the session, stitch and refill the ground pours, then DRC. Needs Java 21
# or later. The jar is downloaded once into .tools/ and checked against the
# sha256 GitHub lists for the release asset.
set -euo pipefail
cd "$(dirname "$0")/.."
version=2.5.0
sha=f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7
jar=".tools/freerouting-$version.jar"
mkdir -p .tools
if [[ ! -s "$jar" ]]; then
  curl -fsSL -o "$jar.part" "https://github.com/freerouting/freerouting/releases/download/v$version/freerouting-$version.jar"
  mv "$jar.part" "$jar"
fi
have="$(shasum -a 256 "$jar" | cut -d' ' -f1)"
[[ "$have" == "$sha" ]] || { echo "$jar: sha256 $have, expected $sha" >&2; exit 1; }

java=java
[[ -x /opt/homebrew/opt/openjdk/bin/java ]] && java=/opt/homebrew/opt/openjdk/bin/java
python=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
[[ -x "$python" ]] || python=python3
kicad="kicad-cli"
command -v kicad-cli >/dev/null || kicad=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

board=hardware/pcb/antuna-remote/antuna-remote.kicad_pcb
finish=hardware/pcb/layout/finish_board.py
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
quiet() { "$@" 2> >(grep -v -e Fontconfig -e wxApp -e 'memory leak' >&2); }
# Freerouting gives the same routes for the same board, and build_board.py
# writes the same board for the same inputs, so one run settles it: a
# route that leaves something unconnected needs a placement change.
quiet "$python" "$finish" "$board" --export "$work/board.dsn"
if ! "$java" -jar "$jar" -de "$work/board.dsn" -do "$work/board.ses" \
  -mt 1 --router.autorouter.max_passes=100 --gui.enabled=false >"$work/freerouting.log" 2>&1; then
  cat "$work/freerouting.log" >&2
  echo "Freerouting failed; $board is still the placed board" >&2
  exit 1
fi
quiet "$python" "$finish" "$board" "$work/board.ses"
if "$kicad" pcb drc --schematic-parity --severity-error --exit-code-violations \
  -o "$work/drc.rpt" "$board" >/dev/null 2>&1; then
  echo "routed $board, DRC clean"
  exit 0
fi
grep -E '^(\*\* Found|\[|    @)' "$work/drc.rpt" >&2
echo "DRC failed; $board holds the route, scripts/build-board.sh restores the placed board" >&2
exit 1
