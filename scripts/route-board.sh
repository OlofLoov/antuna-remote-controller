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
cp "$board" "$work/placed.kicad_pcb"

# Freerouting is not deterministic: a run can leave a net or a ground
# island unconnected. Route again from the placed board until DRC passes.
for attempt in 1 2 3 4 5; do
  cp "$work/placed.kicad_pcb" "$board"
  quiet "$python" "$finish" "$board" --export "$work/board.dsn"
  "$java" -jar "$jar" -de "$work/board.dsn" -do "$work/board.ses" \
    --router.autorouter.max_passes=100 --gui.enabled=false >"$work/freerouting.log" 2>&1
  quiet "$python" "$finish" "$board" "$work/board.ses"
  if "$kicad" pcb drc --severity-error --exit-code-violations -o "$work/drc.rpt" "$board" >/dev/null 2>&1; then
    echo "routed $board, DRC clean (attempt $attempt)"
    exit 0
  fi
  echo "attempt $attempt: $(grep -E '^\*\* Found' "$work/drc.rpt" | tr '\n' ' ')"
done
echo "no clean route in five attempts; $board holds the last one" >&2
exit 1
