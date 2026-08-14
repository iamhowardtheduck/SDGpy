#!/usr/bin/env bash
#
# load-integrations.sh
#
# Installs Elastic integration packages via the Fleet EPM API and (optionally)
# attaches each one to an agent policy as a package policy.
#
#   Packages: windows, proxysg (Broadcom ProxySG), netflow,
#             ti_abusech (AbuseCH), network_traffic (Packet Capture)
#
# Usage:
#   ./load-integrations.sh                  # install packages + create policy + add package policies
#   INSTALL_ONLY=1 ./load-integrations.sh   # only install the package assets into Kibana
#   AGENT_POLICY_ID=abc123 ./load-integrations.sh   # attach to an existing policy
#
set -Eeuo pipefail

# ----------------------------------------------------------------------------
# Config (override with env vars)
# ----------------------------------------------------------------------------
KIBANA_URL="${KIBANA_URL:-https://kb.elastic.lab:443}"
KIBANA_AUTH="${KIBANA_AUTH:-sdg:changeme}"        # user:pass  (or set KIBANA_API_KEY)
KIBANA_API_KEY="${KIBANA_API_KEY:-}"              # if set, used instead of basic auth
INSECURE="${INSECURE:-1}"                         # 1 = curl -k (self-signed lab certs)
PRERELEASE="${PRERELEASE:-true}"                  # proxysg is still beta -> needs true
NAMESPACE="${NAMESPACE:-default}"
POLICY_NAME="${POLICY_NAME:-Lab Collection Policy}"
POLICY_DESC="${POLICY_DESC:-Created by load-integrations.sh}"
AGENT_POLICY_ID="${AGENT_POLICY_ID:-}"
INSTALL_ONLY="${INSTALL_ONLY:-0}"

PACKAGES=(
  windows           # Windows event logs + metrics
  proxysg           # Broadcom ProxySG / Edge SWG access logs (beta)
  netflow           # NetFlow / IPFIX records
  ti_abusech        # abuse.ch threat intel (URLhaus, MalwareBazaar, ThreatFox)
  network_traffic   # Network Packet Capture
)

# ----------------------------------------------------------------------------
# Plumbing
# ----------------------------------------------------------------------------
command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required (apt install jq)"; exit 1; }

CURL_OPTS=(--silent --show-error --location --max-time 300
           --header "kbn-xsrf: true"
           --header "Content-Type: application/json"
           --header "elastic-api-version: 2023-10-31")
[[ "$INSECURE" == "1" ]] && CURL_OPTS+=(--insecure)
if [[ -n "$KIBANA_API_KEY" ]]; then
  CURL_OPTS+=(--header "Authorization: ApiKey ${KIBANA_API_KEY}")
else
  CURL_OPTS+=(--user "$KIBANA_AUTH")
fi

RESP_BODY=""; RESP_CODE=""

# kbn <METHOD> <PATH> [BODY]  -> sets RESP_BODY / RESP_CODE
kbn() {
  local method="$1" path="$2" body="${3:-}" raw
  if [[ -n "$body" ]]; then
    raw=$(curl "${CURL_OPTS[@]}" -w $'\n%{http_code}' -X "$method" "${KIBANA_URL}${path}" -d "$body")
  else
    raw=$(curl "${CURL_OPTS[@]}" -w $'\n%{http_code}' -X "$method" "${KIBANA_URL}${path}")
  fi
  RESP_CODE="${raw##*$'\n'}"
  RESP_BODY="${raw%$'\n'*}"
}

fail() { echo "  ✗ $1"; echo "    HTTP $RESP_CODE: $(echo "$RESP_BODY" | jq -rc '.message // .error // .' 2>/dev/null | cut -c1-300)"; }

# ----------------------------------------------------------------------------
# 0. Connectivity check
# ----------------------------------------------------------------------------
echo "==> Kibana: $KIBANA_URL"
kbn GET "/api/status"
if [[ "$RESP_CODE" != "200" ]]; then
  fail "cannot reach Kibana"; exit 1
fi
echo "    version $(echo "$RESP_BODY" | jq -r '.version.number // "unknown"'), status $(echo "$RESP_BODY" | jq -r '.status.overall.level // .status.overall.state // "unknown"')"

# ----------------------------------------------------------------------------
# 1. Install packages
# ----------------------------------------------------------------------------
declare -A PKG_VERSION=()
echo
echo "==> Installing integration packages"
for pkg in "${PACKAGES[@]}"; do
  # Resolve latest available version from the registry via Kibana
  kbn GET "/api/fleet/epm/packages/${pkg}?prerelease=${PRERELEASE}"
  if [[ "$RESP_CODE" != "200" ]]; then
    echo "  ✗ ${pkg}: not found in the package registry (HTTP $RESP_CODE)"
    echo "    hint: curl -k -u '${KIBANA_AUTH}' '${KIBANA_URL}/api/fleet/epm/packages?prerelease=true' | jq -r '.items[].name' | grep -i <term>"
    continue
  fi
  ver=$(echo "$RESP_BODY" | jq -r '.item.version')
  status=$(echo "$RESP_BODY" | jq -r '.item.status // "not_installed"')
  installed=$(echo "$RESP_BODY" | jq -r '.item.savedObject.attributes.version // .item.installationInfo.version // empty')
  PKG_VERSION["$pkg"]="$ver"

  if [[ "$status" == "installed" && "$installed" == "$ver" ]]; then
    echo "  = ${pkg} ${ver} already installed"
    continue
  fi

  kbn POST "/api/fleet/epm/packages/${pkg}/${ver}" '{"force":true}'
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  + ${pkg} ${ver} installed ($(echo "$RESP_BODY" | jq -r '.items | length') assets)"
  else
    fail "${pkg} ${ver} install failed"
  fi
done

if [[ "$INSTALL_ONLY" == "1" ]]; then
  echo
  echo "INSTALL_ONLY=1 — package assets installed, no policy changes made."
  exit 0
fi

# ----------------------------------------------------------------------------
# 2. Agent policy (create or reuse)
# ----------------------------------------------------------------------------
echo
echo "==> Agent policy"
if [[ -z "$AGENT_POLICY_ID" ]]; then
  kbn POST "/api/fleet/agent_policies?sys_monitoring=true" "$(jq -nc \
      --arg n "$POLICY_NAME" --arg d "$POLICY_DESC" --arg ns "$NAMESPACE" \
      '{name:$n, description:$d, namespace:$ns, monitoring_enabled:["logs","metrics"]}')"
  if [[ "$RESP_CODE" == "200" ]]; then
    AGENT_POLICY_ID=$(echo "$RESP_BODY" | jq -r '.item.id')
    echo "  + created '${POLICY_NAME}' (${AGENT_POLICY_ID}) with system monitoring"
  else
    # Most likely 409 — name already taken. Look it up.
    kbn GET "/api/fleet/agent_policies?kuery=$(printf 'ingest-agent-policies.name:"%s"' "$POLICY_NAME" | jq -sRr @uri)"
    AGENT_POLICY_ID=$(echo "$RESP_BODY" | jq -r '.items[0].id // empty')
    if [[ -z "$AGENT_POLICY_ID" ]]; then
      fail "could not create or find agent policy '${POLICY_NAME}'"; exit 1
    fi
    echo "  = reusing existing '${POLICY_NAME}' (${AGENT_POLICY_ID})"
  fi
else
  echo "  = using AGENT_POLICY_ID=${AGENT_POLICY_ID}"
fi

# Existing package policies on this policy, so re-runs are idempotent
kbn GET "/api/fleet/package_policies?kuery=$(printf 'ingest-package-policies.policy_ids:"%s"' "$AGENT_POLICY_ID" | jq -sRr @uri)&perPage=200"
EXISTING=$(echo "$RESP_BODY" | jq -r '[.items[]?.package.name] | @tsv' 2>/dev/null || echo "")

# ----------------------------------------------------------------------------
# 3. Attach each integration to the policy
# ----------------------------------------------------------------------------
echo
echo "==> Adding package policies"
for pkg in "${PACKAGES[@]}"; do
  ver="${PKG_VERSION[$pkg]:-}"
  [[ -z "$ver" ]] && { echo "  - ${pkg}: skipped (not installed)"; continue; }

  if [[ " $EXISTING " == *" $pkg "* ]]; then
    echo "  = ${pkg} already on this policy"
    continue
  fi

  body=$(jq -nc \
    --arg name "${pkg}-1" \
    --arg ns "$NAMESPACE" \
    --arg pid "$AGENT_POLICY_ID" \
    --arg pkg "$pkg" \
    --arg ver "$ver" \
    '{name:$name, namespace:$ns, policy_id:$pid,
      package:{name:$pkg, version:$ver}, inputs:{}}')

  kbn POST "/api/fleet/package_policies" "$body"
  if [[ "$RESP_CODE" == "200" ]]; then
    echo "  + ${pkg} ${ver} -> $(echo "$RESP_BODY" | jq -r '.item.id')"
  else
    fail "${pkg} package policy failed"
  fi
done

echo
echo "Done. Review inputs at ${KIBANA_URL}/app/fleet/policies/${AGENT_POLICY_ID}"
