#!/usr/bin/env python3
"""Archive a completed batch's evidence in the same layout as the M3 baseline.

Usage: uv run python tools/archive_batch.py jobs/gpt6-followup/gpt-6-sol
Only copies result/config/lock, trajectories, verifier evidence and artifacts;
raw provider debug logs and host environment are not part of the public archive.
"""
import argparse
import json
import shutil
from pathlib import Path

from run_batch import job_result

REPO = Path(__file__).resolve().parent.parent


def archive(source, destination):
    manifest = json.loads((source / "batch-manifest.json").read_text())
    if manifest.get("status") not in ("complete", "complete_with_invalid"):
        raise ValueError("batch must have finished every scheduled slot before archival")
    if destination.exists():
        raise ValueError(f"archive destination already exists: {destination}")
    trials = []
    for slot in manifest["order"]:
        twin, attempt = slot.rsplit("#", 1)
        job = source / f"{twin}__{attempt}"
        result = job_result(job, allow_invalid=True)
        if result is None:
            raise ValueError(f"missing result for {slot}")
        trials.append((job, result))
    destination.mkdir(parents=True)
    shutil.copy2(source / "batch-manifest.json", destination / "batch-manifest.json")
    for job, result in trials:
        target = destination / job.name / result.parent.name
        target.mkdir(parents=True)
        for name in ("result.json", "config.json", "lock.json", "agent/trajectory.json"):
            src = result.parent / name
            if src.is_file():
                dst = target / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        for name in ("artifacts", "verifier"):
            src = result.parent / name
            if src.is_dir():
                shutil.copytree(src, target / name, symlinks=True)
        record = job / "runner-attempt.json"
        if record.exists():
            shutil.copy2(record, target.parent / record.name)
    print(f"Archived {len(trials)} trial slots to {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.source / "batch-manifest.json").read_text())
    destination = args.out or REPO / "results/runs" / manifest["model"].split("/")[-1]
    archive(args.source, destination)


if __name__ == "__main__":
    main()
