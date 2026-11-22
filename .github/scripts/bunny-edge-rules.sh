#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
set +x
set -euo pipefail

: "${BUNNY_API_KEY:?Set the BUNNY_API_KEY repository secret.}"

zone_id=7064266
zone_url="https://api.bunny.net/pullzone/$zone_id"

bunny_api() {
    printf 'AccessKey: %s\n' "$BUNNY_API_KEY" |
        curl --disable --silent --show-error --fail-with-body \
            --connect-timeout 10 --max-time 30 --header @- \
            --header 'Accept: application/json' "$@"
}

zone=$(bunny_api "$zone_url")
changes=$(printf '%s\n' "$zone" |
    jq -er --rawfile headers site/_headers --argjson zone_id "$zone_id" \
        -f .github/scripts/bunny-edge-rules.jq)

while IFS=$'\t' read -r description payload; do
    printf 'Applying %s\n' "$description"
    status=$(bunny_api --json "$payload" --output /dev/null --write-out '%{http_code}' \
        "$zone_url/edgerules/addOrUpdate")
    if [[ $status != 2[0-9][0-9] ]]; then
        printf 'Bunny returned HTTP %s while applying %s.\n' "$status" "$description" >&2
        exit 1
    fi
done <<< "$changes"

check_site() {
    local url=$1 expected_status=$2 expected_redirect=${3:-}
    local response line status redirect

    printf '\n%s\n' "$url"
    if ! response=$(curl --disable -sSI --connect-timeout 10 --max-time 20 \
        --suppress-connect-headers --write-out '%{http_code} %{redirect_url}' "$url"); then
        printf '::warning::Could not read the response headers from %s.\n' "$url"
        return
    fi

    read -r status redirect <<< "${response##*$'\n'}"
    while IFS= read -r line; do
        line=${line%$'\r'}
        case ${line,,} in
            http/*|location:*|content-security-policy:*|referrer-policy:*|x-content-type-options:*|\
            permissions-policy:*|cross-origin-opener-policy:*|strict-transport-security:*|\
            cache-control:*|link:*|content-type:*)
                printf '%s\n' "$line"
                ;;
        esac
    done <<< "${response%$'\n'*}"

    if [[ $status != "$expected_status" ]]; then
        printf '::warning::%s returned HTTP %s (expected %s).\n' "$url" "$status" "$expected_status"
    elif [[ $redirect != "$expected_redirect" ]]; then
        printf '::warning::%s has an unexpected redirect target.\n' "$url"
    fi
}

unset BUNNY_API_KEY
check_site https://fazit.dev/ 200
check_site https://www.fazit.dev/ 301 https://fazit.dev/
