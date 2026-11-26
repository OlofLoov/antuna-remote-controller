#!/usr/bin/env bash
# The checks the pre-push hook runs. Each change that adds a PCB, enclosure
# or firmware check adds its step here and to CI.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

fail=0
step() {
  local name=$1; shift
  printf '== %s\n' "$name"
  "$@" || { printf 'FAILED: %s\n' "$name" >&2; fail=1; }
}

step "spec references" bash scripts/check-spec-refs.sh
if command -v openspec >/dev/null; then
  step "openspec" openspec validate --all --strict --no-interactive
fi
KICAD_CLI=$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)
if [[ -x "$KICAD_CLI" ]]; then
  step "kicad erc" "$KICAD_CLI" sch erc --severity-error --exit-code-violations \
    -o "${TMPDIR:-/tmp}/antuna-erc.rpt" hardware/pcb/antuna-remote/antuna-remote.kicad_sch
  step "kicad drc" "$KICAD_CLI" pcb drc --schematic-parity --severity-error --exit-code-violations \
    -o "${TMPDIR:-/tmp}/antuna-drc.rpt" hardware/pcb/antuna-remote/antuna-remote.kicad_pcb
fi
if command -v shellcheck >/dev/null; then
  step "shellcheck" shellcheck scripts/*.sh scripts/githooks/* .claude/hooks/*.sh
fi

exit "$fail"
