#!/usr/bin/env bash
# Download the vendor documents listed in docs/datasheets/manifest.tsv into
# docs/datasheets/files/, which git ignores. Rows marked "hand" are listed
# with their page so the owner can save them by hand under the given name.
# A pinned sha256 that no longer matches means the vendor changed the file:
# reread it before trusting values taken from the old one.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
manifest="$root/docs/datasheets/manifest.tsv"
dir="$root/docs/datasheets/files"
mkdir -p "$dir"

missing=0
changed=0
# Tabs become US (0x1f) first: read treats a tab as whitespace and would
# merge two tabs around an empty field, shifting the columns after it.
while IFS=$'\x1f' read -r file refs part _kind _rev get url sha; do
  [[ "$file" == "file" || "$file" == "-" ]] && continue
  path="$dir/$file"
  if [[ ! -s "$path" && "$get" == "auto" ]]; then
    tmp="$path.part"
    if curl -fsSL --retry 2 -o "$tmp" "$url" && head -c 5 "$tmp" | grep -q '%PDF-'; then
      mv "$tmp" "$path"
      echo "fetched  $file"
    else
      rm -f "$tmp"
      echo "FAILED   $file ($refs, $part): save it by hand from $url"
      missing=$((missing + 1))
      continue
    fi
  fi
  if [[ ! -s "$path" ]]; then
    echo "BY HAND  $file ($refs, $part): $url"
    missing=$((missing + 1))
    continue
  fi
  have="$(shasum -a 256 "$path" | cut -d' ' -f1)"
  if [[ -z "$sha" ]]; then
    echo "unpinned $file sha256 $have"
  elif [[ "$have" != "$sha" ]]; then
    echo "CHANGED  $file: manifest $sha, file $have"
    changed=$((changed + 1))
  fi
done < <(tr '\t' '\037' < "$manifest")

echo "$missing to save by hand, $changed changed"
[[ "$changed" -eq 0 ]]
