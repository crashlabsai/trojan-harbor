# Seven-model comparison figures

These figures visualize the archived September 15 and October 4, 2026 batches.
They use [summary.json](../summary.json), [trials.csv](../trials.csv), and the
model order in [batch-config.json](../batch-config.json). No new model calls
are made when rendering them.

| Figure | Vector | Raster |
|---|---|---|
| Attack success and secure task completion | [SVG](attack-outcomes.svg) | [PNG](attack-outcomes.png) |
| Successful attacks by family | [SVG](attack-families.svg) | [PNG](attack-families.png) |
| Median/p95 runtime and estimated cost | [SVG](performance-cost.svg) | [PNG](performance-cost.png) |

## Reproduce

From the repository root:

```bash
uv run --script tools/plot_results.py
```

The script declares its Matplotlib dependency in inline metadata, keeping it
separate from the frozen benchmark dependencies. It uses Matplotlib's bundled
DejaVu fonts, embeds glyphs in the SVGs, and writes PNGs at 180 DPI. It checks
the summary against individual trial records before plotting, including model
sets, outcome counts, median/p95 latency, estimated costs, and five valid
attack trials per family. Model order and axes are consistent across figures;
bar-chart axes start at zero.

## Reading the figures

- Outcome figures use 40 valid attack trials per model. Secure completion
  requires both legitimate task success and no attacker success. Clean
  controls are reported in the README table and full report.
- Heatmap cells show successful attacks out of five attempts. Trials without
  observed payload exposure remain in the denominator, including one Terra
  release-remote trial. The shading is a discrete count scale from zero to five.
- Runtime endpoints are the median and 95th percentile, not confidence
  intervals. Time and estimated cost include all 80 attempts, including the
  single invalid GPT-6 Luna clean trial.
- The hatched GPT-5.6 Sol cost bar retains the original conservative rate
  estimate without a cache discount. Other rows use documented batch rates.
  These estimates are not invoices or uniformly repriced costs.
- The results cover eight fixed attack families with five repetitions each.
  Historical timing, provider aliases, default reasoning, and host load limit
  comparisons; zero observed compromises do not establish general immunity.

See the [full comparison](../report.md) and [outcome review](../review.md)
for the underlying tables, exposure details, and interpretation limits.
