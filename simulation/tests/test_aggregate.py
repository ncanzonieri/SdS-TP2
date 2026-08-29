import numpy as np
import pandas as pd

from src.aggregate import Detector, detect_onset, detect_run, ensemble, steady_mean


def _series(t_end=400, va_onset=80, s_onset=160):
    t = np.arange(t_end + 1)
    va = np.where(t < va_onset, 0.1 + 0.8 * (t / va_onset), 0.9)
    s = np.where(t < s_onset, 0.2 + 0.6 * (t / s_onset), 0.85)
    return pd.DataFrame({"t": t, "va": va, "S": s})


def _d(window, atol, rtol, t_min, sustain):
    return Detector(window=window, atol=atol, rtol=rtol, t_min=t_min, sustain=sustain)


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
    va_ss = steady_mean(frame["t"].to_numpy(), frame["va"].to_numpy(), rec["t_onset_va"])
    s_ss = steady_mean(frame["t"].to_numpy(), frame["S"].to_numpy(), rec["t_onset_S"])
    assert va_ss > 0.8
    assert s_ss > 0.7


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
    index = pd.DataFrame(
        [
            {
                "model": "vicsek",
                "rho": 2.0,
                "eta": 0.0,
                "T": 400,
                "seed": 1,
                "repeat": 0,
                "N": 4,
                "L": 10,
                "run_dir": "r1",
                "batch": "b",
                "series_path": "x",
                "dynamic_path": "",
            }
        ]
    )
    frame = _series()

    def load(_row):
        return frame

    _onset, agg = ensemble(index, load, Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3))
    assert int(agg.iloc[0]["n_runs_va"]) == 1
    assert np.isnan(agg.iloc[0]["va_ss_std"])
