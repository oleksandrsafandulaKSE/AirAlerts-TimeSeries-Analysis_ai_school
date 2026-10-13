"""The single final-test scoring (M4 plan §4): joint pre-registration, hash binding, access marker, guard."""
import dataclasses
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import run_all
from src import data, evaluate
from tests.test_run_all import cfg as fixture_cfg, fixture

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def fitted(tmp_path, monkeypatch):
    monkeypatch.setattr(run_all.grid, "check_base_rate", lambda g, before, H: 0.0)
    p, n = fixture(tmp_path)
    c1 = fixture_cfg(n, 0)
    configs = {"official": c1, "official_h3": dataclasses.replace(c1, name="official_h3", H=pd.Timedelta(hours=3))}
    root = tmp_path / "reports"
    for name, c in configs.items():
        run_all.run_pipeline(c, p, root / name)
    return root, p, configs


def test_refuses_without_both_preregistrations(fitted):
    root, p, configs = fitted
    (root / "official_h3" / "preregistration.json").unlink()
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)
    assert not (root / run_all.JOINT_MARKER).exists()          # nothing read, no marker


def test_marker_written_before_any_test_label(fitted, monkeypatch):
    root, p, configs = fitted
    seen = []
    real = evaluate.split_bounds

    def spy(cfg, split, allow_test=False):
        if split == "test":
            seen.append((root / run_all.JOINT_MARKER).exists())
        return real(cfg, split, allow_test)
    monkeypatch.setattr(run_all.evaluate, "split_bounds", spy)
    run_all.score_final_test(root, p, configs)
    assert seen == [True, True]
    marker = json.loads((root / run_all.JOINT_MARKER).read_text())
    assert set(marker["preregistration_sha256"]) == {"official", "official_h3"}


def test_reproduction_and_tamper_detection(fitted, monkeypatch):
    root, p, configs = fitted
    run_all.score_final_test(root, p, configs)
    m1 = (root / "official" / "metrics.csv").read_text()
    run_all.score_final_test(root, p, configs)                  # same pre-registration -> identical metrics
    assert (root / "official" / "metrics.csv").read_text() == m1
    cal = root / "official_h3" / "calibrator.json"
    original = cal.read_text()
    cal.write_text(original.replace("}", ', "x": 1}'))          # artifact changed after pre-registration
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)
    cal.write_text(original)
    monkeypatch.setattr(run_all, "code_fingerprint", lambda root=None: "changed")
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)


def test_new_preregistration_after_access_is_refused(fitted, monkeypatch):
    root, p, configs = fitted
    run_all.score_final_test(root, p, configs)
    pr = root / "official" / "preregistration.json"
    d = json.loads(pr.read_text())
    d["best_iteration"] += 1                                     # a "new" predictor pre-registered after the test
    pr.write_text(json.dumps(d, indent=2, sort_keys=True))
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)


def test_outputs_and_identical_keys(fitted):
    root, p, configs = fitted
    res = run_all.score_final_test(root, p, configs)
    for name in configs:
        t = res[name]
        assert {"model", "recent_rate", "climatology", "persistence_raw", "persistence_calibrated"} <= set(t.baseline)
        assert t.groupby("group")["rows"].nunique().eq(1).all()  # every predictor on the same rows
        for f in ("metrics.csv", "metrics.json", "reliability.png", "calibration_in_the_large.csv"):
            assert (root / name / f).exists()


def test_only_score_final_test_unlocks_the_test():
    hits = []
    for path in list((ROOT / "src").glob("*.py")) + [ROOT / "scripts" / "run_all.py"]:
        for i, line in enumerate(path.read_text().splitlines()):
            if re.search(r"\w\([^)]*allow_test\s*=\s*True", line) and "def " not in line:  # calls only
                hits.append((path.name, line.strip()))
    assert hits == [("run_all.py", 'a, b = evaluate.split_bounds(cfg, "test", allow_test=True)')]


def test_refit_after_access_is_refused(fitted):
    root, p, configs = fitted
    run_all.score_final_test(root, p, configs)
    with pytest.raises(data.DataQualityError):
        run_all.run_pipeline(configs["official"], p, root / "official")


def test_new_regime_is_bound_to_the_frozen_predictor(fitted):
    from src import config
    root, p, configs = fitted
    run_all.score_final_test(root, p, configs)
    pr = root / "official" / "preregistration.json"
    d = json.loads(pr.read_text())
    d["note"] = "re-registered after the test"
    pr.write_text(json.dumps(d, indent=2, sort_keys=True))
    with pytest.raises(data.DataQualityError, match="frozen at the final test"):
        run_all.run_new_regime(config.new_regime(), root / "new_regime", root, p)


def test_preregistration_must_hash_every_artifact(fitted):
    root, p, configs = fitted
    pr = root / "official" / "preregistration.json"
    d = json.loads(pr.read_text())
    del d["sha256"]["model.txt"]
    pr.write_text(json.dumps(d, indent=2, sort_keys=True))
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)
    assert not (root / run_all.JOINT_MARKER).exists()


def test_reproduce_validation_is_enforced(fitted, tmp_path):
    """A consistent-looking but different model (hash updated) must fail the validation reproduction."""
    root, p, configs = fitted
    d = root / "official"
    other = root / "official_h3" / "model.txt"
    (d / "model.txt").write_text(other.read_text())
    pr = json.loads((d / "preregistration.json").read_text())
    pr["sha256"]["model.txt"] = run_all.model.sha256_file(d / "model.txt")
    (d / "preregistration.json").write_text(json.dumps(pr, indent=2, sort_keys=True))
    with pytest.raises(data.DataQualityError):
        run_all.score_final_test(root, p, configs)


def test_headline_predictor_is_scored(fitted, monkeypatch):
    root, p, configs = fitted
    monkeypatch.setattr(run_all.model.Predictor, "headline", lambda self, df: np.full(len(df), 0.25))
    monkeypatch.setattr(run_all, "_reproduce_validation", lambda run_dir, predictor: None)
    res = run_all.score_final_test(root, p, configs)
    m = res["official"].set_index(["baseline", "group"]).loc[("model", "overall")]
    yb = m["base_rate"]
    assert m["brier"] == pytest.approx(yb * 0.75 ** 2 + (1 - yb) * 0.25 ** 2)


def test_new_regime_checks_frozen_files_and_source(fitted, monkeypatch):
    from src import config
    root, p, configs = fitted
    run_all.score_final_test(root, p, configs)
    mt = root / "official" / "model.txt"
    original = mt.read_text()
    mt.write_text(original + "\n")
    with pytest.raises(data.DataQualityError, match="sha256 differs from the pre-registration"):
        run_all.run_new_regime(config.new_regime(), root / "nr", root, p)
    mt.write_text(original)
    mixed = pd.DataFrame({"source": ["api", "official"], "unit": ["kyiv_city"] * 2})
    monkeypatch.setattr(run_all.data, "load_api", lambda *a, **k: mixed)
    with pytest.raises(data.DataQualityError, match="source"):
        run_all.run_new_regime(config.new_regime(), root / "nr", root, p)
