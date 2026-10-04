# GPT-5.6 Luna and Terra extension

This batch adds the Luna generation preceding GPT-6 (`gpt-5.6-luna`) and the
latest documented Terra (`gpt-5.6-terra`) to the existing model comparison.
Both identities and current prices were checked against official OpenAI model
pages and the full catalog on October 4, 2026. The authenticated API model list
also contained both; it listed no newer Terra.

Sources: [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
[all models](https://developers.openai.com/api/docs/models/all),
[release log](https://developers.openai.com/api/docs/changelog).

Both batches are complete: 160 valid trials, no invalids or retries. Luna's
attack-success rate was 16/40; Terra's was 15/40. Both passed 40/40 clean
controls. See the [seven-model comparison](report.md),
[outcome and exposure review](review.md), [trial data](trials.csv), and
[audit manifest](manifest.json).

## Protocol

Each model receives the same 80 scheduled slots as the previous batches:
8 families × attack/clean twins × 5 attempts. Task bytes, graders, the Harbor
revision and dependency pins remain frozen. Submission seed is 20260915,
concurrency is three per model, the turn limit is 60, summarization is disabled,
and reasoning/temperature overrides are omitted. Both models document medium
as their provider-default reasoning setting. The two model batches run
concurrently. The $50/model launch guard remains unchanged.

Completed invalid trials are retained without retry, with their recorded
costs, while remaining slots continue. Invalids never become zero-attack grades.
Missing or malformed records still stop the driver. Model aliases, provider
load and host contention are not fixed across batches, so timing comparisons
have those practical limits.

The extended comparison includes all seven evaluated models. September 15
GPT-5.6 Sol and GPT-6 Astra are historical baselines; the other five models
were run on October 4. Existing evidence and reports are preserved.

## Reproduce

With Docker and the host OpenAI credential configured as in the repository
README, run this command once for each of `gpt-5.6-luna` and `gpt-5.6-terra`:

```bash
model=gpt-5.6-luna
uv run python tools/run_batch.py \
  --config results/luna-terra-followup/batch-config.json \
  --model "openai/$model" --ceiling-usd 50 \
  --seed 20260915 --concurrency 3 \
  --out "jobs/luna-terra-followup/$model" --continue-on-trial-error
uv run python tools/archive_batch.py "jobs/luna-terra-followup/$model"
```

Add `--resume` to the batch command only when continuing that exact recorded
plan. The runner returns nonzero when invalid trials exist, including when all
scheduled slots have finished; consult the manifest's status. Archival accepts
completed batches with retained invalids and refuses to overwrite existing
archives. Use fresh output directories for a replication.

```bash
uv run python tools/compare_models.py \
  --config results/luna-terra-followup/batch-config.json \
  --out results/luna-terra-followup results/runs
uv run python tools/exposure.py results/runs \
  --output results/luna-terra-followup/exposure.json
```

## Cost accounting

The new batches use current standard short-context rates per million tokens:

| Model | Input | Cached input | Output |
|---|---:|---:|---:|
| GPT-5.6 Luna | $0.20 | $0.02 | $1.20 |
| GPT-5.6 Terra | $2.00 | $0.20 | $12.00 |

The old unused rate-table entries predated the July 30 price reductions and
have been corrected. Historical GPT-5.6 Sol costs retain the original M3
conservative estimate, explicitly labeled in the comparison. Recorded LiteLLM
costs are shown separately. Neither estimate is an invoice.
