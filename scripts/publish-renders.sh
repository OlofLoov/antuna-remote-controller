#!/usr/bin/env bash
# Copy the PNGs in <outdir> to <dest> on the renders branch and push, then
# print a Markdown block that shows them. Run by CI, which sets GITHUB_TOKEN
# and GITHUB_REPOSITORY. Main commits go to main/<date>-<sha>/, pull request
# commits to pr-<number>/<sha>/. The renders branch has no history in common
# with main, so build outputs never enter main.
set -euo pipefail

out="$(cd "${1:?usage: publish-renders.sh <outdir> <dest>}" && pwd)"
dest="${2:?usage: publish-renders.sh <outdir> <dest>}"
repo="${GITHUB_REPOSITORY:?}"
url="https://x-access-token:${GITHUB_TOKEN:?}@github.com/$repo.git"

work="$(mktemp -d)"
cd "$work"
git init -q
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git remote add origin "$url"

# Several commits can publish at once. Each writes its own folder, so a
# retry on top of the newer branch never conflicts.
for attempt in 1 2 3 4 5; do
  if git fetch -q --depth 1 origin renders 2>/dev/null; then
    git checkout -q -B renders FETCH_HEAD
  else
    git checkout -q --orphan renders
    git rm -rqf . 2>/dev/null || true
  fi
  mkdir -p "$dest"
  cp "$out"/*.png "$dest"/
  {
    echo "# Renders"
    echo
    echo "One folder per commit, made by \`scripts/render.sh\` in CI."
    echo "Newest main commits first."
    echo
    for dir in $(find main -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort -r); do
      echo "## ${dir#main/}"
      echo
      for png in "$dir"/*.png; do
        echo "![$(basename "$png" .png)]($png)"
      done
      echo
    done
  } > README.md
  git add -A
  git commit -qm "Renders for $dest"
  if git push -q origin renders; then
    break
  fi
  [[ "$attempt" -eq 5 ]] && { echo "push failed five times" >&2; exit 1; }
  sleep $((attempt * 3))
done

raw="https://raw.githubusercontent.com/$repo/renders/$dest"
for png in "$out"/*.png; do
  name="$(basename "$png")"
  echo "**${name%.png}**"
  echo
  echo "![${name%.png}]($raw/$name)"
  echo
done
