# Reproducing the post-Astra GPT-6 comparison

The [batch configuration](batch-config.json) records the three new models found
in official OpenAI documentation on October 4, 2026: GPT-6 Sol and GPT-6 Luna
(September 22), and GPT-6.1 Sol (September 29). The authenticated API model list
also contained these three and GPT-6 Astra; no other GPT-6 IDs appeared.

Sources: [release log](https://developers.openai.com/api/docs/changelog),
[model catalog](https://developers.openai.com/api/docs/models),
[Sol](https://developers.openai.com/api/docs/models/gpt-6-sol),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), and
[6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol).
[Daybreak Blue](https://developers.openai.com/api/docs/models/gpt-daybreak-blue-latest)
is a specialized alias with different safeguards, not another GPT-6 base model.
Fast/Ultrafast and Pro are processing/reasoning modes, outside this model comparison.

The experiment repeats M3's 80-slot design for each new model: all 16 task twins,
five trials each, the same seed (20260915), three workers per model, 60 turns,
summarization disabled, and no temperature/reasoning override. The task source,
graders, instructions, pinned Harbor revision, and locked dependencies are
unchanged. The baseline is the archived Astra batch from September 15.
This is a historical comparison; it cannot hold provider load or model aliases
constant across dates. The original M3 artifacts and configuration remain intact.

## Run

Requires Docker Compose v2, buildx >= 0.17, Python 3.12 and uv. Set
`OPENAI_API_KEY` (or the existing `OPENAI_KEY` fallback) in the host environment.
The key stays in the host-side harness; task containers have no public egress.

```bash
uv sync --frozen
uv run pytest checks/ -q -rs

# Run once per model, with separate output roots. The recorded experiment
# ran these three model batches concurrently, with three workers each.
for model in gpt-6-sol gpt-6-luna gpt-6.1-sol; do
  uv run python tools/run_batch.py \
    --config results/gpt6-followup/batch-config.json \
    --model "openai/$model" --ceiling-usd 50 \
    --seed 20260915 --concurrency 3 \
    --out "jobs/gpt6-followup/$model" --continue-on-trial-error
done
```

The $50/model limit is the same conservative launch guard as M3. It stops new
launches when projected spend reaches the threshold; already-running requests
can finish, so it is not a provider-enforced hard billing limit.

The runner stops on errors by default. `--continue-on-trial-error` retains a
completed trial exception or invalid grade and continues other scheduled slots,
without retrying the invalid trial. A missing/malformed result or process
failure still stops launches. The runner exits nonzero if any trial was invalid,
even after all slots were attempted. Resume a stopped run with the same arguments
plus `--resume`; prior costs and invalid records are retained. Do not replace
invalid trials with fresh samples.

The original driver required two orchestration repairs: recognize Harbor's
job-level `result.json` separately from its trial result, and permit the
repository's already-committed project-name/description change while still
checking all task bytes and dependency pins against `v1.0.1-suite`. Neither
repair changes agent prompts, tools, budgets or grading.

## Archive and measure

```bash
for model in gpt-6-sol gpt-6-luna gpt-6.1-sol; do
  uv run python tools/archive_batch.py "jobs/gpt6-followup/$model"
done
uv run python tools/compare_models.py \
  results/runs/gpt-6-astra results/runs/gpt-6-sol \
  results/runs/gpt-6-luna results/runs/gpt-6.1-sol
uv run python tools/exposure.py \
  results/runs/gpt-6-astra results/runs/gpt-6-sol \
  results/runs/gpt-6-luna results/runs/gpt-6.1-sol \
  --output results/gpt6-followup/exposure.json
```

Archival refuses to overwrite an existing destination. Use `--out` for a fresh
replication. The comparison emits `report.md`, `summary.json`, and `trials.csv`,
checks task checksums and explicit agent settings, flags incomplete trial cells,
and keeps invalid trials out of the outcome denominators. Missing telemetry is
reported as missing. The per-trial CSV includes invalid attempts and their costs.

Metrics: attack/clean utility, attack success, secure utility, clean background
attack, observed payload exposure, per-family Wilson intervals, agent/API/full
trial latency, input/output/cache tokens, and estimated/recorded API cost.
Clean failures require trajectory review before calling them refusals.
