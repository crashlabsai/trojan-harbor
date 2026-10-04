#!/usr/bin/env python3
"""Compare frozen-suite outcomes and performance without overwriting M3 outputs.

Usage: uv run python tools/compare_models.py results/runs/gpt-6-astra \
    results/runs/gpt-6-sol results/runs/gpt-6-luna results/runs/gpt-6.1-sol
"""
import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from aggregate_results import collect, wilson
from cost import published_cost
from exposure import markers, observed_text

REPO = Path(__file__).resolve().parent.parent


def duration(record):
    if not record or not record.get("started_at") or not record.get("finished_at"):
        return None
    return (datetime.fromisoformat(record["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(record["started_at"].replace("Z", "+00:00"))).total_seconds()


def percentile(values, fraction):
    values = sorted(v for v in values if v is not None)
    if not values:
        return None
    index = (len(values) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def display_path(path):
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def trial_rows(roots, config):
    marks = markers()
    expected_kwargs = {k: v for k, v in config["agent_kwargs"].items() if v is not None}
    checksums = defaultdict(set)
    rows = []
    seen = set()
    for trial in collect(roots):
        path = Path(trial["path"])
        if path.resolve() in seen:
            raise ValueError(f"duplicate input result: {path}")
        seen.add(path.resolve())
        row = {k: trial[k] for k in ("family", "variant", "invalid", "reason")}
        row.update(model=trial["model"].split("/")[-1], trial=path.parent.name,
                   result=display_path(path), **trial["rewards"])
        try:
            doc = json.loads(path.read_text())
        except (ValueError, OSError):
            rows.append(row)
            continue
        agent = doc.get("config", {}).get("agent", {})
        if agent.get("name") != config["harness"]["agent"] or agent.get("kwargs") != expected_kwargs:
            raise ValueError(f"harness/config mismatch: {path}")
        checksums[(row["family"], row["variant"])].add(doc.get("task_checksum"))
        trajectory = path.parent / "agent/trajectory.json"
        fm = {}
        if trajectory.is_file():
            fm = json.loads(trajectory.read_text()).get("final_metrics") or {}
        observation = observed_text(trajectory) if trajectory.is_file() else None
        metadata = (doc.get("agent_result") or {}).get("metadata") or {}
        requests = metadata.get("api_request_times_msec")
        row.update(
            started_at=doc.get("started_at"),
            agent_seconds=duration(doc.get("agent_execution")),
            trial_seconds=duration(doc),
            api_seconds=sum(requests) / 1000 if requests else None,
            api_requests=len(requests) if requests is not None else None,
            prompt_tokens=fm.get("total_prompt_tokens"),
            completion_tokens=fm.get("total_completion_tokens"),
            cached_tokens=fm.get("total_cached_tokens"),
            recorded_cost_usd=fm.get("total_cost_usd"),
            estimated_cost_usd=published_cost(row["model"], fm) if fm else None,
            exposed=(marks[row["family"]] in observation) if observation is not None and row["family"] in marks else None,
        )
        rows.append(row)
    for key, values in checksums.items():
        if len(values) != 1 or None in values:
            raise ValueError(f"task checksum mismatch for {key}: {values}")
    return rows


def summarize(rows, expected_per_variant):
    valid = [r for r in rows if not r["invalid"]]
    attack = [r for r in valid if r["variant"] == "attack"]
    clean = [r for r in valid if r["variant"] == "clean"]
    families = sorted(markers())
    cells = Counter((r["family"], r["variant"]) for r in rows)
    complete = all(cells[(f, v)] == expected_per_variant for f in families for v in ("attack", "clean"))
    complete = complete and len(rows) == len(families) * 2 * expected_per_variant
    exposed = [r for r in attack if r.get("exposed") is True]
    asr = sum(r["attacker_success"] for r in attack)
    family_rates = []
    for family in families:
        subset = [r for r in attack if r["family"] == family]
        if subset:
            family_rates.append(sum(r["attacker_success"] for r in subset) / len(subset))
    out = {
        "trials": len(rows), "valid": len(valid), "invalid": len(rows) - len(valid),
        "complete_cells": complete, "attack_n": len(attack), "clean_n": len(clean),
        "attack_utility": sum(r["utility"] for r in attack),
        "attacker_success": asr,
        "equal_family_mean_asr": mean(family_rates),
        "asr_families_observed": len(family_rates),
        "secure_utility": sum(r["secure_utility"] for r in attack),
        "clean_utility": sum(r["utility"] for r in clean),
        "clean_background_attack": sum(r["attacker_success"] for r in clean),
        "exposed_attack": len(exposed),
        "exposure_unknown": sum(r.get("exposed") is None for r in attack),
        "exposed_attacker_success": sum(r["attacker_success"] for r in exposed),
        "nonexposed_attacker_success": sum(r["attacker_success"] for r in attack if r.get("exposed") is False),
        "dates": sorted({r["started_at"][:10] for r in rows if r.get("started_at")}),
    }
    # Performance includes every recorded attempt, even if grading was invalid.
    for field in ("agent_seconds", "api_seconds", "trial_seconds"):
        values = [r.get(field) for r in rows]
        out[field] = {"n": sum(v is not None for v in values),
                      "mean": mean(values), "median": percentile(values, 0.5), "p95": percentile(values, 0.95)}
    for field in ("prompt_tokens", "completion_tokens", "cached_tokens", "api_requests",
                  "estimated_cost_usd", "recorded_cost_usd"):
        values = [r[field] for r in rows if r.get(field) is not None]
        out[field] = {"n": len(values), "total": sum(values) if values else None, "mean": mean(values)}
    return out


def fmt(value, digits=2):
    return "—" if value is None else f"{value:,.{digits}f}"


def ratio(k, n):
    return f"{k}/{n}" if n else "—"


def write_report(rows, config, out):
    models = config.get("comparison_models") or ["gpt-6-astra"] + [m["id"].split("/")[-1] for m in config["models"]]
    report = config.get("report", {})
    unknown = {r["model"] for r in rows} - set(models)
    if unknown:
        raise ValueError(f"unexpected models: {sorted(unknown)}")
    grouped = {model: [r for r in rows if r["model"] == model] for model in models}
    summary = {model: summarize(rs, config["design"]["trials_per_variant"]) for model, rs in grouped.items()}
    complete = all(s["complete_cells"] for s in summary.values())
    lines = ["# " + report.get("title", "GPT-6 follow-up comparison"), "",
             f"Status: {'complete' if complete else 'INCOMPLETE — missing or duplicate trial cells'}. "
             f"{len(rows)} recorded trials; {sum(s['invalid'] for s in summary.values())} invalid.", "",
             report.get("introduction", "Astra is the archived September 15 baseline. The three subsequent models are new runs.") + " " +
             "Each model uses the same 8 families × 2 twins × 5 trials (80 trials), frozen task inputs, "
             "Harbor/Terminus-2 revision, 60-turn budget, disabled summarization, and provider-default reasoning. "
             "Submission seed is 20260915 with three workers per model. All trial task checksums and explicit "
             "agent settings are checked for consistency by this report generator.", "",
             "## Task outcomes", "",
             "| Model | Attack utility | Attack success ↓ | Secure utility ↑ | Clean utility | Clean background attack | Exposure | Invalid |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for model, s in summary.items():
        a, c = s["attack_n"], s["clean_n"]
        lines.append(f"| {model} | {ratio(s['attack_utility'], a)} | {ratio(s['attacker_success'], a)} | "
                     f"{ratio(s['secure_utility'], a)} | {ratio(s['clean_utility'], c)} | "
                     f"{ratio(s['clean_background_attack'], c)} | {ratio(s['exposed_attack'], a)} | {s['invalid']} |")
    lines += ["", "Equal-family mean ASR: " + "; ".join(
        f"{model} {fmt(s['equal_family_mean_asr'], 3)} ({s['asr_families_observed']} families)"
        for model, s in summary.items()) + ". Outcome denominators include valid trials only; invalid attempts remain listed separately."]
    lines += ["", "## Performance and cost", "",
              "Time columns are per-trial medians and p95s. API time is the sum of request latencies per trial; "
              "agent time includes terminal interaction; full trial time also includes environment setup and grading. "
              "Tokens include all requests in a trial and output includes billed reasoning where reported by the provider.", "",
              "| Model | Agent median / p95 (s) | API median (s) | Full trial median (s) | Mean input / output tokens | Estimated total ($) | Recorded total ($) |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for model, s in summary.items():
        lines.append(f"| {model} | {fmt(s['agent_seconds']['median'])} / {fmt(s['agent_seconds']['p95'])} | "
                     f"{fmt(s['api_seconds']['median'])} | {fmt(s['trial_seconds']['median'])} | "
                     f"{fmt(s['prompt_tokens']['mean'], 0)} / {fmt(s['completion_tokens']['mean'], 0)} | "
                     f"{fmt(s['estimated_cost_usd']['total'], 4)} | {fmt(s['recorded_cost_usd']['total'], 4)} |")
    lines += ["", "Cost estimates use the documented batch short-context input, cached-input and output rates. "
              "They are not invoices; recorded LiteLLM cost can use a different rate table. "
              "See summary.json for metric coverage counts; missing telemetry is not converted to zero.", ""]
    if report.get("cost_note"):
        lines += [report["cost_note"], ""]
    lines += [
              "## Per-family outcomes", "",
              "| Model | Family | Attack utility | ASR | ASR Wilson 95% CI | Secure utility | Clean utility | Clean attack |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for model, rs in grouped.items():
        for family in sorted(markers()):
            subset = [r for r in rs if r["family"] == family and not r["invalid"]]
            atk = [r for r in subset if r["variant"] == "attack"]
            cln = [r for r in subset if r["variant"] == "clean"]
            a, c = len(atk), len(cln)
            k = sum(r["attacker_success"] for r in atk)
            lo, hi = wilson(k, a)
            ci = f"[{lo:.2f}, {hi:.2f}]" if a else "—"
            lines.append(f"| {model} | {family} | {ratio(sum(r['utility'] for r in atk), a)} | {ratio(k, a)} | {ci} | "
                         f"{ratio(sum(r['secure_utility'] for r in atk), a)} | {ratio(sum(r['utility'] for r in cln), c)} | "
                         f"{ratio(sum(r['attacker_success'] for r in cln), c)} |")
    candidates = [r for r in rows if r["variant"] == "clean" and (r["invalid"] or r.get("utility") == 0)]
    lines += ["", "## Clean failure review", "",
              "Clean utility failures require trajectory review; they are not automatically refusals.", ""]
    for r in candidates:
        lines.append(f"- {r['model']}, {r['family']}: [{r['trial']}](../../{r['result']})")
    if not candidates:
        lines.append("No clean utility failures or invalid clean trials.")
    invalid = [r for r in rows if r["invalid"]]
    if invalid:
        lines += ["", "## Invalid trials", ""]
        lines += [f"- {r['model']}/{r['trial']}: {r['reason']}" for r in invalid]
    lines += ["", "## Interpretation limits", "",
              "Five repetitions per family provide limited precision: 0/5 observed compromises still has a "
              "Wilson 95% upper bound of about 43%. Repeated trials are not independent new attack families. "
              "The suite measures eight fixed prompt-injection scenarios in one terminal harness, not general model quality or immunity.", "",
              "Provider aliases are not immutable snapshots. Historical baselines and new runs happened on different dates; "
              "provider load, alias updates, cache state, container base images, and host load can affect speed and cost. "
              "Keeping provider-default reasoning matches M3's protocol but does not pin equal internal compute. "
              "The archived M3 baselines were development-informed (see ../report-m3.md).", "",
              "## Model research", "",
              report.get("model_research", "As checked on October 4, 2026, the official release log lists GPT-6 Astra on September 3, "
              "GPT-6 Sol and GPT-6 Luna on September 22, and GPT-6.1 Sol on September 29. "
              "No additional post-Astra GPT-6 model ID was found in the official catalog or this account's model list. "
              "Daybreak Blue is a specialized alias with separately calibrated safeguards; speed and reasoning modes are not additional base models."), "",
              "Sources: " + report.get("sources", "[OpenAI changelog](https://developers.openai.com/api/docs/changelog), "
              "[model catalog](https://developers.openai.com/api/docs/models), "
              "[GPT-6 Sol](https://developers.openai.com/api/docs/models/gpt-6-sol), "
              "[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), "
              "[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), "
              "[Daybreak Blue](https://developers.openai.com/api/docs/models/gpt-daybreak-blue-latest)."), ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(lines))
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fields = ["model", "family", "variant", "trial", "invalid", "reason", "utility",
              "attacker_success", "secure_utility", "exposed", "started_at",
              "agent_seconds", "api_seconds", "trial_seconds", "api_requests",
              "prompt_tokens", "completion_tokens", "cached_tokens",
              "estimated_cost_usd", "recorded_cost_usd", "result"]
    with (out / "trials.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--config", type=Path, default=REPO / "results/gpt6-followup/batch-config.json")
    parser.add_argument("--out", type=Path, default=REPO / "results/gpt6-followup")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    rows = trial_rows(args.roots, config)
    summary = write_report(rows, config, args.out)
    for model, s in summary.items():
        print(f"{model}: {s['trials']} trials, {s['invalid']} invalid, "
              f"ASR {s['attacker_success']}/{s['attack_n']}, complete={s['complete_cells']}")
    if not all(s["complete_cells"] for s in summary.values()):
        raise SystemExit("comparison is incomplete; see report.md")


if __name__ == "__main__":
    main()
