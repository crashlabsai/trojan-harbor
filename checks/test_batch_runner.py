"""Fail-closed invariants for the metered M3 batch driver."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_batch", REPO / "tools" / "run_batch.py")
run_batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_batch)


def test_only_frozen_models_are_accepted():
    assert run_batch.validate_model("openai/gpt-6-astra") == "gpt-6-astra"
    assert run_batch.validate_model("openai/gpt-5.6-sol") == "gpt-5.6-sol"
    with pytest.raises(ValueError, match="not frozen"):
        run_batch.validate_model("openai/gpt-4.1-mini")


def test_seeded_plan_has_every_twin_five_times():
    plan = run_batch.build_plan([], 5, 20260915)
    assert len(plan) == 80
    assert len(set(plan)) == 80
    assert plan == run_batch.build_plan([], 5, 20260915)
    assert plan != run_batch.build_plan([], 5, 20260916)


def test_job_result_requires_exactly_one_parseable_result(tmp_path):
    assert run_batch.job_result(tmp_path) is None
    trial = tmp_path / "trial"
    trial.mkdir()
    result = trial / "result.json"
    valid = {
        "task_name": "pi-eval/example-attack",
        "exception_info": None,
        "verifier_result": {
            "rewards": {"utility": 1, "attacker_success": 0, "secure_utility": 1}
        },
    }
    result.write_text(json.dumps(valid))
    (tmp_path / "result.json").write_text(json.dumps({"n_total_trials": 1, "stats": {}}))
    assert run_batch.job_result(tmp_path) == result
    other = tmp_path / "other"
    other.mkdir()
    (other / "result.json").write_text(json.dumps(valid))
    with pytest.raises(ValueError, match="2 result files"):
        run_batch.job_result(tmp_path)


def test_job_result_rejects_invalid_reward(tmp_path):
    trial = tmp_path / "trial"
    trial.mkdir()
    (trial / "result.json").write_text(json.dumps({
        "task_name": "pi-eval/example-attack",
        "exception_info": None,
        "verifier_result": {
            "rewards": {"utility": 1, "attacker_success": 1, "secure_utility": 1}
        },
    }))
    with pytest.raises(ValueError, match="invalid rewards"):
        run_batch.job_result(tmp_path)
    assert run_batch.job_result(tmp_path, allow_invalid=True) == trial / "result.json"


def test_frozen_runtime_inputs_match_tag():
    assert run_batch.validate_frozen_suite() == run_batch.CONFIG["suite_commit"]


def test_branding_changes_allowed_but_dependency_drift_rejected():
    before = '[project]\nname="old"\ndescription="old"\ndependencies=["a==1"]\n'
    after = before.replace('"old"', '"new"')
    assert run_batch.runtime_manifest(before, "pyproject.toml") == run_batch.runtime_manifest(after, "pyproject.toml")
    assert run_batch.runtime_manifest(before, "pyproject.toml") != run_batch.runtime_manifest(after.replace("a==1", "a==2"), "pyproject.toml")
    lock = '[[package]]\nname="old"\nsource={virtual="."}\n[[package]]\nname="a"\nversion="1"\n'
    assert run_batch.runtime_manifest(lock, "uv.lock") == run_batch.runtime_manifest(lock.replace('"old"', '"new"'), "uv.lock")
    assert run_batch.runtime_manifest(lock, "uv.lock") != run_batch.runtime_manifest(lock.replace('version="1"', 'version="2"'), "uv.lock")


def test_followup_uses_same_protocol_and_separate_model_list():
    config = json.loads((REPO / "results/gpt6-followup/batch-config.json").read_text())
    for key in ("suite_version", "suite_commit", "harness", "agent_kwargs"):
        assert config[key] == run_batch.CONFIG[key]
    for model in ("gpt-6-sol", "gpt-6-luna", "gpt-6.1-sol"):
        assert run_batch.validate_model("openai/" + model, config) == model
        with pytest.raises(ValueError, match="not frozen"):
            run_batch.validate_model("openai/" + model)
    assert config["design"]["seed"] == run_batch.CONFIG["actual"]["seed"]
    assert config["design"]["concurrency_per_model"] == run_batch.CONFIG["actual"]["concurrency_per_model"]


def test_resume_preserves_invalid_slot_and_spend_without_retry(tmp_path, monkeypatch):
    config = tmp_path / "config.json"
    config.write_text(json.dumps(run_batch.CONFIG))
    out = tmp_path / "batch"
    monkeypatch.setattr(run_batch, "validate_frozen_suite", lambda config: config["suite_commit"])
    plan = [("vendor-support-attack", 1), ("vendor-support-clean", 1)]
    monkeypatch.setattr(run_batch, "build_plan", lambda *args: plan)
    launched = []

    def fake_harbor(command, **kwargs):
        job = Path(command[command.index("-o") + 1])
        launched.append(job.name)
        trial = job / "trial"
        (trial / "agent").mkdir(parents=True)
        bad = "attack" in job.name
        doc = {"task_name": job.name.split("__")[0],
               "exception_info": {"exception_type": "ValueError"} if bad else None,
               "verifier_result": None if bad else {"rewards": {"utility": 1, "attacker_success": 0, "secure_utility": 1}}}
        (trial / "result.json").write_text(json.dumps(doc))
        (job / "result.json").write_text(json.dumps({"n_total_trials": 1, "stats": {}}))
        (trial / "agent/trajectory.json").write_text(json.dumps({"final_metrics": {
            "total_prompt_tokens": 1000, "total_completion_tokens": 100}}))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(run_batch.subprocess, "run", fake_harbor)
    argv = ["run_batch.py", "--config", str(config), "--model", "openai/gpt-6-astra",
            "--ceiling-usd", "50", "--out", str(out), "--concurrency", "1",
            "--continue-on-trial-error"]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        run_batch.main()
    assert exc.value.code == 1  # Invalid outcomes remain visible to automation.
    first = json.loads((out / "batch-manifest.json").read_text())
    assert first["status"] == "complete_with_invalid"
    assert (first["completed"], first["invalid"]) == (2, 1)
    assert first["spent_usd"] == pytest.approx(0.03)
    monkeypatch.setattr(sys, "argv", argv + ["--resume"])
    with pytest.raises(SystemExit):
        run_batch.main()
    resumed = json.loads((out / "batch-manifest.json").read_text())
    assert len(launched) == 2
    assert resumed["spent_usd"] == first["spent_usd"]
    assert resumed["attempts"] == first["attempts"]
