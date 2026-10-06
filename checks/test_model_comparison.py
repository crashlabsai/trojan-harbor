"""Accounting and comparability invariants for the follow-up report."""
import json

import pytest

from compare_models import percentile, summarize, trial_rows


def test_missing_telemetry_and_trials_are_not_zero_performance():
    summary = summarize([], 5)
    assert not summary["complete_cells"]
    assert summary["agent_seconds"]["median"] is None
    assert summary["estimated_cost_usd"]["total"] is None
    assert summary["estimated_cost_usd"]["n"] == 0


def test_invalid_trials_do_not_enter_outcome_denominators():
    rows = [
        {"family": "vendor-support", "variant": "attack", "invalid": False,
         "utility": 1, "attacker_success": 1, "secure_utility": 0, "exposed": True},
        {"family": "vendor-support", "variant": "attack", "invalid": True},
    ]
    summary = summarize(rows, 5)
    assert (summary["trials"], summary["valid"], summary["invalid"]) == (2, 1, 1)
    assert summary["attack_n"] == 1
    assert summary["attacker_success"] == 1
    assert summary["exposed_attack"] == 1
    assert summary["equal_family_mean_asr"] == 1
    assert summary["asr_families_observed"] == 1


def test_percentiles_ignore_missing_and_interpolate():
    assert percentile([None, 10, 20, 30], 0.5) == 20
    assert percentile([10, 20, 30], 0.95) == 29
    assert percentile([None], 0.95) is None


def test_mixed_task_inputs_and_agent_settings_rejected(tmp_path):
    config = {"agent_kwargs": {"max_turns": 60, "reasoning_effort": None},
              "harness": {"agent": "terminus-2"}}
    doc = {
        "task_name": "pi-eval/vendor-support-attack", "task_checksum": "a",
        "agent_info": {"name": "terminus-2", "model_info": {"name": "gpt-6-sol"}},
        "config": {"agent": {"name": "terminus-2", "kwargs": {"max_turns": 60}}},
        "verifier_result": {"rewards": {"utility": 1, "attacker_success": 0, "secure_utility": 1}},
    }
    first = tmp_path / "one"
    first.mkdir()
    (first / "result.json").write_text(json.dumps(doc))
    second = tmp_path / "two"
    second.mkdir()
    doc["task_checksum"] = "b"
    (second / "result.json").write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="checksum mismatch"):
        trial_rows([tmp_path], config)
    doc["task_checksum"] = "a"
    doc["config"]["agent"]["kwargs"]["max_turns"] = 10
    (second / "result.json").write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="harness/config mismatch"):
        trial_rows([tmp_path], config)
    with pytest.raises(ValueError, match="duplicate input"):
        trial_rows([first, first], config)
