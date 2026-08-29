import numpy as np
import pandas as pd
import pytest

from src.aggregate import Detector, detect_onset, detect_run, ensemble, steady_mean


def _series(t_end=400, va_onset=80, s_onset=160):
    t = np.arange(t_end + 1)
    va = np.where(t < va_onset, 0.1 + 0.8 * (t / va_onset), 0.9)
    s = np.where(t < s_onset, 0.2 + 0.6 * (t / s_onset), 0.85)
    return pd.DataFrame({"t": t, "va": va, "S": s})


def _d(window, atol, rtol, t_min, sustain):
    return Detector(window=window, atol=atol, rtol=rtol, t_min=t_min, sustain=sustain)


def _index_row(run_dir, seed=1):
    return {
        "model": "vicsek",
        "rho": 2.0,
        "eta": 0.0,
        "T": 400,
        "seed": seed,
        "repeat": 0,
        "N": 4,
        "L": 10,
        "run_dir": run_dir,
        "batch": "b",
        "series_path": "x",
        "dynamic_path": "",
    }


def test_known_plateau():
    t = np.arange(0, 400)
    y = np.where(t < 80, 0.1, 0.9)
    onset = detect_onset(t, y, _d(20, 0.02, 0.05, 10, 3))
    assert onset.status == "ok"
    assert onset.t_onset is not None
    assert 10 <= onset.t_onset <= 80 + 40


def test_noise_never():
    rng = np.random.default_rng(0)
    t = np.arange(0, 300)
    y = rng.normal(0.5, 0.2, size=t.size)
    onset = detect_onset(t, y, _d(20, 0.001, 0.0, 10, 3))
    assert onset.status == "never"
    assert onset.t_onset is None


def test_too_short():
    t = np.arange(10)
    y = np.ones(10)
    onset = detect_onset(t, y, _d(20, 0.02, 0.05, 5, 3))
    assert onset.status == "too_short"


def test_default_detector_accepts_t500_series():
    t = np.arange(501)
    y = np.full(t.size, 0.8)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert onset.t_onset == 100


def test_sustain_rejects_single_pass():
    t = np.arange(0, 200)
    y = 0.001 * t
    y[80:120] = y[79]
    one = detect_onset(t, y, _d(10, 0.01, 0.0, 5, 1))
    three = detect_onset(t, y, _d(10, 0.01, 0.0, 5, 3))
    assert one.status == "ok"
    assert three.status in {"ok", "never"}
    if three.status == "ok" and one.t_onset is not None and three.t_onset is not None:
        assert three.t_onset >= one.t_onset


def test_dual_onset_independent():
    frame = _series()
    det = Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3)
    rec = detect_run(frame, det)
    assert rec["status_va"] == "ok"
    assert rec["status_S"] == "ok"
    assert rec["t_onset_va"] != rec["t_onset_S"]
    va_ss, _va_std = steady_mean(frame["t"].to_numpy(), frame["va"].to_numpy(), rec["t_onset_va"])
    s_ss, _s_std = steady_mean(frame["t"].to_numpy(), frame["S"].to_numpy(), rec["t_onset_S"])
    assert va_ss > 0.8
    assert s_ss > 0.7


def test_steady_mean_temporal_std_on_plateau():
    t = np.arange(0, 8)
    y = np.array([0.1, 0.1, 0.2, 0.9, 1.1, 0.8, 1.0, 0.7])
    t_onset = 3
    mean, temporal_std = steady_mean(t, y, t_onset)
    tail = y[t >= t_onset]
    assert mean == pytest.approx(float(np.mean(tail)))
    assert temporal_std == pytest.approx(float(np.std(tail, ddof=1)))


def test_atol_changes_onset():
    t = np.arange(0, 300)
    y = 0.9 - 0.4 * np.exp(-t / 80.0)
    loose = detect_onset(t, y, _d(20, 0.05, 0.0, 10, 3))
    tight = detect_onset(t, y, _d(20, 0.001, 0.0, 10, 3))
    assert loose.status == "ok"
    if tight.status == "ok":
        assert tight.t_onset >= loose.t_onset
    else:
        assert tight.status == "never"


def test_ensemble_n1_no_std():
    index = pd.DataFrame([_index_row("r1")])
    frame = _series()

    def load(_row):
        return frame

    _onset, agg = ensemble(index, load, Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3))
    assert int(agg.iloc[0]["n_runs_va"]) == 1
    assert np.isnan(agg.iloc[0]["va_ss_std"])
    assert np.isfinite(agg.iloc[0]["va_ss_err"])


def test_ensemble_err_is_mean_temporal_std_not_variance_or_sem():
    t = np.arange(0, 20)
    t_onset = 10
    base_tail = np.array([0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8])
    offsets = (0.0, 0.001, 0.002)
    frames = {}
    rows = []
    for i, offset in enumerate(offsets):
        run_dir = f"r{i}"
        va = np.concatenate([np.full(10, 0.1), base_tail + offset])
        frames[run_dir] = pd.DataFrame({"t": t, "va": va, "S": np.full(t.size, 0.5)})
        rows.append(_index_row(run_dir, seed=i + 1))

    def load(row):
        return frames[row["run_dir"]]

    _onset, agg = ensemble(pd.DataFrame(rows), load, Detector(), t_onset=t_onset)
    expected_err = float(np.mean([np.std(base_tail + offset, ddof=1) for offset in offsets]))
    err = float(agg.iloc[0]["va_ss_err"])
    std = float(agg.iloc[0]["va_ss_std"])
    n = int(agg.iloc[0]["n_runs_va"])
    assert n == len(offsets)
    assert err == pytest.approx(expected_err)
    assert not np.isclose(err, std**2)
    assert not np.isclose(err, std / np.sqrt(n))
