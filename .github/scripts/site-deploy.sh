#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
set -euo pipefail

: "${BUNNY_STORAGE_PASSWORD:?Set the BUNNY_STORAGE_PASSWORD repository secret.}"
curl_options=(--disable --fail-with-body --silent --show-error --globoff --max-time 60)

storage_request() {
  curl "${curl_options[@]}" --header "AccessKey: $BUNNY_STORAGE_PASSWORD" "$@"
}

storage_url() {
  jq -nr --arg path "$1" '
    "https://storage.bunnycdn.com/fazit-site/" + ($path | split("/") | map(@uri) | join("/"))
  '
}

content_type() {
  case "${1,,}" in
    *.html) printf '%s' 'text/html; charset=utf-8' ;;
    *.css) printf '%s' 'text/css; charset=utf-8' ;;
    *.js|*.mjs) printf '%s' 'text/javascript; charset=utf-8' ;;
    *.txt) printf '%s' 'text/plain; charset=utf-8' ;;
    *.xml) printf '%s' 'application/xml; charset=utf-8' ;;
    *) file --brief --mime-type -- "$1" ;;
  esac
}

list_remote_files() {
  local directory="$1" url listing name
  url=$(storage_url "$directory")
  listing=$(storage_request "$url")
  jq -js '
    if length != 1 or (.[0] | type) != "array" then
      error("Invalid Bunny Storage directory listing")
    else .[0][] end
    | .ObjectName as $name
    | if ($name | type != "string" or . == "" or . == "." or . == ".." or
          contains("/") or contains("\u0000")) or (.IsDirectory | type != "boolean") then
        error("Invalid Bunny Storage directory entry")
      else (if .IsDirectory then $name + "/" else $name end), "\u0000" end
  ' <<< "$listing" |
    while IFS= read -r -d '' name; do
      if [[ "$name" == */ ]]; then
        list_remote_files "$directory$name"
      else
        printf '%s\0' "$directory$name"
      fi
    done
}

# Publish the new files before pruning old ones.
find site -type f ! -name '*.py' ! -name '*.pyc' ! -path 'site/generate_og.mjs' ! -path 'site/_headers' \
  ! -path 'site/.htaccess' ! -name '*.license' -print0 |
  while IFS= read -r -d '' file; do
    url=$(storage_url "${file#site/}")
    mime=$(content_type "$file")
    storage_request --request PUT --header "Content-Type: $mime" \
      --upload-file "$file" --output /dev/null "$url"
  done

# Finish listing every directory before deleting any files.
remote_files=$(mktemp)
trap 'rm -f -- "$remote_files"' EXIT
list_remote_files '' > "$remote_files"
while IFS= read -r -d '' path; do
  if [[ ! -f "site/$path" ]]; then
    url=$(storage_url "$path")
    storage_request --request DELETE --output /dev/null "$url"
  fi
done < "$remote_files"

# Clear cached copies after the storage zone is up to date.
if [[ -n "${BUNNY_API_KEY:-}" ]]; then
  curl "${curl_options[@]}" --request POST --header "AccessKey: $BUNNY_API_KEY" \
    --header 'Content-Type: application/json' --data '{}' --output /dev/null \
    'https://api.bunny.net/pullzone/7064266/purgeCache'
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    printf '%s\n' 'purged=true' >> "$GITHUB_OUTPUT"
  fi
else
  printf '%s\n' '::notice::The CDN cache was not purged because BUNNY_API_KEY is unset.'
fi
