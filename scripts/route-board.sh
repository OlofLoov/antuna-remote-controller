#!/usr/bin/env bash
# Route the board with Freerouting: export Specctra DSN, autoroute, import
# the session, refill the ground pours. Needs Java 21 or later. The jar is
# downloaded once into .tools/ and checked against the sha256 GitHub lists
# for the release asset.
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

board=hardware/pcb/antuna-remote/antuna-remote.kicad_pcb
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
"$python" - "$board" "$work/board.dsn" <<'PY' 2> >(grep -v -e Fontconfig -e wxApp >&2)
import sys, pcbnew
board = pcbnew.LoadBoard(sys.argv[1])
for track in list(board.GetTracks()):
    board.Remove(track)
assert pcbnew.ExportSpecctraDSN(board, sys.argv[2])
PY
"$java" -jar "$jar" -de "$work/board.dsn" -do "$work/board.ses" -mp 100 --gui.enabled=false
"$python" - "$board" "$work/board.ses" <<'PY' 2> >(grep -v -e Fontconfig -e wxApp >&2)
import sys, pcbnew
board = pcbnew.LoadBoard(sys.argv[1])
for track in list(board.GetTracks()):
    board.Remove(track)
assert pcbnew.ImportSpecctraSES(board, sys.argv[2])
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(sys.argv[1], board)
PY
echo "routed $board"
