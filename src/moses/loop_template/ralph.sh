#!/usr/bin/env bash
#
# ralph.sh — the RALPH harness for a Moses improvement campaign.
#
# This script drives the autonomous loop. Each iteration it:
#   1. Judges the target and writes a fresh verdict.json into the state dir.
#   2. Hands prompt.md + verdict.json to a coding engine (claude / codex).
#   3. Verifies the engine produced a clean, single, non-regressing commit.
#   4. Appends an audit record to campaign.json (via check_invariants.py).
#
# It is intentionally defensive: any failure in a single iteration is logged and
# the loop continues (up to the iteration / time budget) rather than aborting the
# whole campaign.
#
# Configuration arrives entirely through the environment (set by loop_runner):
#   MOSES_WORKTREE        absolute path to the worktree being improved
#   MOSES_STATE_DIR       absolute path to the .moses state dir
#   MOSES_ENGINE          auto | claude | codex
#   MOSES_MAX_ITERATIONS  integer, max iterations this run
#   MOSES_MAX_HOURS       float, wall-clock budget (0 = unlimited)
#   MOSES_COOLDOWN        seconds to sleep between iterations
#   MOSES_BIN             path to the `moses` executable (or a python fallback)

set -euo pipefail

# --------------------------------------------------------------------------- #
# Configuration & defaults
# --------------------------------------------------------------------------- #

WORKTREE="${MOSES_WORKTREE:-$(pwd)}"
STATE_DIR="${MOSES_STATE_DIR:-${WORKTREE}/.moses}"
ENGINE="${MOSES_ENGINE:-auto}"
MAX_ITERATIONS="${MOSES_MAX_ITERATIONS:-10}"
MAX_HOURS="${MOSES_MAX_HOURS:-0}"
COOLDOWN="${MOSES_COOLDOWN:-5}"
MOSES_BIN="${MOSES_BIN:-moses}"

CAMPAIGN="${STATE_DIR}/campaign.json"
PROMPT="${STATE_DIR}/prompt.md"
LOG="${STATE_DIR}/loop.log"
VERDICT="${STATE_DIR}/verdict.json"
AFTER="${STATE_DIR}/after.json"
CHECKER="${STATE_DIR}/check_invariants.py"

START_EPOCH="$(date +%s)"

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "${LOG}" >&2; }

die() { log "FATAL: $*"; exit 1; }

# --------------------------------------------------------------------------- #
# Pre-flight
# --------------------------------------------------------------------------- #

[ -d "${WORKTREE}" ] || die "worktree not found: ${WORKTREE}"
[ -f "${CAMPAIGN}" ] || die "campaign not found: ${CAMPAIGN} (run loop init)"
[ -f "${PROMPT}" ]   || die "prompt not found: ${PROMPT}"

cd "${WORKTREE}"

TARGET_PATH="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("target_path","src/"))' "${CAMPAIGN}")"

resolve_engine() {
  if [ "${ENGINE}" != "auto" ]; then echo "${ENGINE}"; return; fi
  if command -v claude >/dev/null 2>&1; then echo "claude"; return; fi
  if command -v codex  >/dev/null 2>&1; then echo "codex";  return; fi
  echo "none"
}

ENGINE="$(resolve_engine)"
log "engine=${ENGINE} target=${TARGET_PATH} max_iter=${MAX_ITERATIONS} max_hours=${MAX_HOURS}"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

judge_into() {
  # $1 = output json path
  "${MOSES_BIN}" judge "${TARGET_PATH}" --json "$1" --quiet || true
}

score_of()  { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["score"])' "$1"; }
grade_of()  { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["grade"])' "$1"; }
viol_of()   {
  python3 - "$1" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
print(sum(len(c.get("violations", [])) for c in v["commandments"] if c.get("status") == "measured"))
PY
}

time_exceeded() {
  local now budget_s elapsed
  budget_s="$(python3 -c "print(int(float('${MAX_HOURS}')*3600))")"
  # A budget of 0 (from "0", "0.0", any zero form) means "no time limit".
  [ "${budget_s}" -le 0 ] && return 1
  now="$(date +%s)"
  elapsed=$(( now - START_EPOCH ))
  [ "${elapsed}" -ge "${budget_s}" ]
}

run_engine() {
  # Hands the prompt + verdict to the coding engine. The engine is expected to
  # edit files and commit. If no engine is available we no-op so the harness can
  # still be exercised (the iteration will simply record "no change").
  local instructions
  instructions="$(cat "${PROMPT}")
Verdict file: ${VERDICT}
Write any scratch results to ${AFTER}."
  case "${ENGINE}" in
    claude)
      claude -p "${instructions}" --permission-mode acceptEdits >>"${LOG}" 2>&1 || true
      ;;
    codex)
      codex exec "${instructions}" >>"${LOG}" 2>&1 || true
      ;;
    none)
      log "no coding engine available; skipping edit step"
      ;;
  esac
}

# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #

iteration=0
while [ "${iteration}" -lt "${MAX_ITERATIONS}" ]; do
  if time_exceeded; then log "time budget reached; stopping"; break; fi
  iteration=$(( iteration + 1 ))
  log "=== iteration ${iteration}/${MAX_ITERATIONS} ==="

  # 1. Baseline verdict for this iteration.
  judge_into "${VERDICT}"
  [ -f "${VERDICT}" ] || { log "judge produced no verdict; aborting iteration"; continue; }
  before_score="$(score_of "${VERDICT}")"
  before_viol="$(viol_of "${VERDICT}")"
  before_commit="$(git rev-parse HEAD)"
  log "before: score=${before_score} violations=${before_viol} @ ${before_commit:0:8}"

  # 2. Let the engine attempt one improvement.
  run_engine

  # 3. Did anything change?
  if git diff --quiet && git diff --cached --quiet; then
    log "no changes this iteration; cooling down"
    sleep "${COOLDOWN}"
    continue
  fi

  # 4. Re-judge to verify the change is an improvement.
  judge_into "${AFTER}"
  after_score="$(score_of "${AFTER}")"
  after_viol="$(viol_of "${AFTER}")"

  regressed="false"
  if python3 -c "import sys; sys.exit(0 if float('${after_score}') >= float('${before_score}') and int('${after_viol}') <= int('${before_viol}') else 1)"; then
    log "improved: score ${before_score} -> ${after_score}, violations ${before_viol} -> ${after_viol}"
  else
    regressed="true"
    log "REGRESSION: score ${before_score} -> ${after_score}, violations ${before_viol} -> ${after_viol}; reverting"
    git reset --hard "${before_commit}" >>"${LOG}" 2>&1 || true
    git clean -fd >>"${LOG}" 2>&1 || true
    sleep "${COOLDOWN}"
    continue
  fi

  # 5. Commit if the engine did not already.
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "moses: iteration ${iteration} — automated improvement" >>"${LOG}" 2>&1 || true
  fi
  after_commit="$(git rev-parse HEAD)"

  # 6. Record the audit trail.
  python3 "${CHECKER}" record \
    --campaign "${CAMPAIGN}" \
    --iteration "${iteration}" \
    --commit "${after_commit}" \
    --score-before "${before_score}" \
    --score-after "${after_score}" \
    --violations-before "${before_viol}" \
    --violations-after "${after_viol}" \
    --grade-after "$(grade_of "${AFTER}")" \
    >>"${LOG}" 2>&1 || log "warning: failed to record iteration ${iteration}"

  log "committed @ ${after_commit:0:8}"
  sleep "${COOLDOWN}"
done

# Final validation of the whole campaign.
python3 "${CHECKER}" validate --campaign "${CAMPAIGN}" --repo "${WORKTREE}"
status=$?
log "campaign complete: ${iteration} iteration(s), check_invariants exit=${status}"
exit "${status}"
