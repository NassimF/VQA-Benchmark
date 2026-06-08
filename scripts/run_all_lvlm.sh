#!/usr/bin/env bash
# Run all 4 Video LLM baselines sequentially.
# Stops immediately if any model fails or produces fewer results than the benchmark expects.
# Progress and errors are logged to logs/lvlm_run.log.
# Resume-safe: each model picks up from its checkpoint if interrupted.

set -euo pipefail

PYTHON=/root/miniconda3/envs/vqa-benchmark/bin/python
LOG_DIR="$(dirname "$0")/../logs"
LOG="$LOG_DIR/lvlm_run.log"
RESULTS_DIR="$(dirname "$0")/../data/benchmark"
BENCHMARK="$(dirname "$0")/../data/benchmark/benchmark_v1.json"
EXPECTED=$($PYTHON -c "
import json, sys
bm = json.load(open('$BENCHMARK'))
pairs = [q for q in bm['qa_pairs'] if q.get('answerable', True) and q.get('ground_truth_spans')]
print(len(pairs))
" 2>/dev/null || echo 0)

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

check_results() {
    local model="$1"
    local file="$RESULTS_DIR/lvlm_results_${model//-/_}.json"
    if [ ! -f "$file" ]; then
        log "ERROR: output file not found: $file"
        return 1
    fi
    local count
    count=$($PYTHON -c "import json; print(json.load(open('$file'))['n_pairs'])" 2>/dev/null || echo 0)
    if [ "$count" -lt "$EXPECTED" ]; then
        log "ERROR: $model produced $count results (expected $EXPECTED)"
        return 1
    fi
    log "OK: $model — $count results saved"
    return 0
}

run_model() {
    local model="$1"
    log "===== START $model ====="
    if $PYTHON scripts/run_lvlm_baseline.py --model "$model" >> "$LOG" 2>&1; then
        if check_results "$model"; then
            log "===== DONE $model ====="
            return 0
        fi
    fi
    log "===== FAILED $model — stopping pipeline ====="
    return 1
}

log "Pipeline started. Models: qwen2-vl-7b → video-llava-7b → mplug-owl3-8b → llava-13b"

# qwen2-vl-7b already complete — skip if results file exists with enough entries
if check_results qwen2-vl-7b 2>/dev/null; then
    log "qwen2-vl-7b already complete, skipping."
else
    run_model qwen2-vl-7b
fi

if check_results video-llava-7b 2>/dev/null; then
    log "video-llava-7b already complete, skipping."
else
    run_model video-llava-7b
fi
run_model mplug-owl3-8b
run_model llava-13b

log "All 4 models complete. Next: python scripts/compute_text_metrics.py --results data/benchmark/lvlm_results_{model}.json"
