#!/usr/bin/env bash
# One-time local setup. Safe to re-run.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath scripts/githooks
chmod +x scripts/*.sh scripts/githooks/* .claude/hooks/*.sh
echo "git hooks path -> scripts/githooks"
command -v gh >/dev/null || echo "note: brew install gh (needed to open PRs)"
command -v openspec >/dev/null || echo "note: npm install -g @fission-ai/openspec@1.16.0 (specs and changes live in openspec/)"
command -v shellcheck >/dev/null || echo "note: brew install shellcheck (CI runs it)"
command -v actionlint >/dev/null || echo "note: brew install actionlint (CI runs it)"
command -v kicad-cli >/dev/null || [[ -x /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli ]] ||
    echo "note: brew install --cask kicad (KiCad 10.0.8, runs ERC in scripts/fast-checks.sh)"
command -v rsvg-convert >/dev/null || echo "note: brew install librsvg (scripts/render.sh turns the schematic into a PNG)"
[[ -x /opt/homebrew/opt/openjdk/bin/java ]] || command -v java >/dev/null || echo "note: brew install openjdk (scripts/route-board.sh runs Freerouting)"
