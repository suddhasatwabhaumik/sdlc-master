# Automated E2E Shell Test Suite Guide (`tests/e2e_<feature_name>/`)

This reference defines the mandatory structure, fail-closed honesty rules, and bash templates for **Goldfish Remediator 4C (Automated E2E Shell Harness Worker)** in [`pr-feature-branch-review`](../SKILL.md) and [`sdlc-master-orchestrator`](../../sdlc-master-orchestrator/SKILL.md).

---

## 1. Core E2E Honesty & Isolation Mandates

1. **Zero Silent Mock Fallbacks (Fail-Closed Honesty)**:
   - Never allow an E2E script to catch a live service/agent/database failure, fall back to a mock payload, and exit `0` with `[PASS]`.
   - Require an explicit `--mode=live` vs. `--mode=hermetic` flag (or `E2E_MODE` env var). In `live` mode, missing credentials or unreachable endpoints must fail immediately with exit code `1`.
2. **Zero Hardcoded Environment Constants**:
   - Inject all project IDs, base URLs, ports, and test credentials via environment variables (`${TARGET_PROJECT_ID:?}`, `${SERVICE_URL:-http://127.0.0.1:8080}`) or CLI arguments.
3. **Strict Bash Safety & Cleanup**:
   - Every script must begin with `set -euo pipefail`.
   - Register a `trap cleanup EXIT` handler if background processes or temporary scratch files (`mktemp -d`) are spawned.

---

## 2. Standard 4-Script Modular Layout

Package repeatable E2E verification scripts under `tests/e2e_<feature_name>/`:

| Script File | Verification Focus | Key Assertions |
| :--- | :--- | :--- |
| `test_1_security_and_auth.sh` | Cryptographic Auth, Backdoor Rejection & RBAC | Rejects unauthenticated (`401`), `mock-token-*` (`401`), forged/expired JWTs (`401`), and non-admin callers on privileged routes (`403`). |
| `test_2_core_business_logic.sh` | Core Feature Workflows & Tenant Isolation | Verifies happy-path state transitions, response headers, idempotency, malformed payload rejection (`422`), and strict cross-tenant isolation. |
| `test_3_concurrency_and_metrics.sh` | Concurrency Limits, Resource Cleanup & Telemetry | Fires parallel requests to verify single-point concurrency slot acquisition, `429 Too Many Requests` (`Retry-After`), lock release, and OpenTelemetry metrics. |
| `test_4_domain_integration.sh` | Real Runtime / Agent / Cloud Integration | Validates end-to-end integration against the target `{{DOMAIN_STACK}}` runtime or `${TARGET_PROJECT_ID:?}` with fail-closed honesty. |
| `run_all_<feature_name>_tests.sh` | Master Orchestrator & ASCII Scorecard | Runs `test_1` through `test_4` sequentially, records pass/fail timings, prints an ASCII summary table, and exits `0` only if 100% pass. |

---

## 3. Master Runner Template (`run_all_<feature_name>_tests.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="${1:-${TARGET_PROJECT_ID:-}}"
E2E_MODE="${E2E_MODE:-hermetic}"

if [[ "${E2E_MODE}" == "live" && -z "${PROJECT_ID}" ]]; then
  echo "[FAIL] TARGET_PROJECT_ID or CLI arg #1 is required when E2E_MODE=live" >&2
  exit 1
fi

declare -a SUITES=(
  "test_1_security_and_auth.sh"
  "test_2_core_business_logic.sh"
  "test_3_concurrency_and_metrics.sh"
  "test_4_domain_integration.sh"
)

PASS_COUNT=0
FAIL_COUNT=0
declare -a RESULTS=()

for suite in "${SUITES[@]}"; do
  suite_path="${SCRIPT_DIR}/${suite}"
  if [[ ! -x "${suite_path}" ]]; then
    chmod +x "${suite_path}"
  fi
  echo "----------------------------------------------------------------"
  echo "Running ${suite} (mode=${E2E_MODE})..."
  if TARGET_PROJECT_ID="${PROJECT_ID}" E2E_MODE="${E2E_MODE}" "${suite_path}"; then
    RESULTS+=("| ${suite} | [PASS] |")
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    RESULTS+=("| ${suite} | [FAIL] |")
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

echo ""
echo "+------------------------------------------+--------+"
echo "| E2E Test Suite                           | Status |"
echo "+------------------------------------------+--------+"
for row in "${RESULTS[@]}"; do
  printf "%s\n" "${row}"
done
echo "+------------------------------------------+--------+"
echo "Summary: ${PASS_COUNT} passed, ${FAIL_COUNT} failed."

[[ "${FAIL_COUNT}" -eq 0 ]]
```
