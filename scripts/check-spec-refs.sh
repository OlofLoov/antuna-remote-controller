#!/usr/bin/env bash
# Fails when a test or a bench log cites a requirement that does not exist.
# A citation is <capability>/<requirement-slug>, where the slug is the
# requirement name lowercased with each run of other characters turned into
# one hyphen. A requirement exists when it is in openspec/specs, or in the
# ADDED or MODIFIED section of an active change's delta spec. Citations of
# the app repo (antenna:<capability>/<slug>) are not checked here.
set -euo pipefail
cd "$(dirname "$0")/.."

valid=$(mktemp)
cited=$(mktemp)
trap 'rm -f "$valid" "$cited"' EXIT

slugs() {
    while IFS= read -r name; do
        slug=$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')
        printf '%s/%s\n' "$1" "$slug"
    done
}

{
    for spec in openspec/specs/*/spec.md; do
        [ -e "$spec" ] || continue
        sed -n 's/^### Requirement: //p' "$spec" | slugs "$(basename "$(dirname "$spec")")"
    done
    for delta in openspec/changes/*/specs/*/spec.md; do
        [ -e "$delta" ] || continue
        awk '/^## /{keep = /^## (ADDED|MODIFIED) Requirements/} keep && sub(/^### Requirement: /, "")' "$delta" |
            slugs "$(basename "$(dirname "$delta")")"
    done
} | sort -u >"$valid"

capabilities=$(cut -d/ -f1 "$valid" | sort -u | paste -sd'|' -)
if [ -z "$capabilities" ]; then
    echo "ok: no requirements yet, nothing to cite"
    exit 0
fi

pattern="(^|[^a-z0-9/:-])($capabilities)/[a-z0-9][a-z0-9-]*"
{
    grep -rhoE "$pattern" firmware --include='*.c' --include='*.h' --include='*.py' 2>/dev/null || true
    grep -rhoE "$pattern" hardware --include='*.py' --exclude-dir=.venv 2>/dev/null || true
    grep -rhoE "$pattern" docs/bench --include='*.md' 2>/dev/null || true
} | sed -E 's/^[^a-z]*//' | sort -u >"$cited"

missing=$(comm -23 "$cited" "$valid")
if [ -n "$missing" ]; then
    echo "These citations name no requirement in openspec/specs or an active change:"
    printf '%s\n' "$missing"
    exit 1
fi
echo "ok: all $(wc -l <"$cited" | tr -d ' ') cited requirements exist"
