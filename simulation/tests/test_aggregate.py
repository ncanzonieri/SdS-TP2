import numpy as np
import pandas as pd
import pytest

from src.aggregate import (
    Detector,
    detect_onset,
    detect_run,
    ensemble,
    moving_average,
    onset_report,
    steady_mean,
)


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


def test_moving_average_covers_forward_window():
    y = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    assert np.allclose(moving_average(y, 2), [0.5, 1.5, 2.5, 3.5])
    assert np.allclose(moving_average(y, 1), y)


def test_known_plateau_onset_sits_at_the_step():
    t = np.arange(0, 400)
    y = np.where(t < 80, 0.1, 0.9)
    onset = detect_onset(t, y, _d(20, 0.02, 0.05, 10, 10))
    assert onset.status == "ok"
    assert 80 <= onset.t_onset <= 100
    assert onset.band_lo < 0.9 < onset.band_hi


def test_smooth_rise_onset_waits_for_the_plateau():
    """Regresion: con t_min=100 fijo, una serie que todavia sube a t=100 se
    promediaba desde ahi. t0 tiene que esperar a que la serie llegue al plateau."""
    t = np.arange(0, 2001)
    y = 0.98 - 0.9 * np.exp(-t / 50.0)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    # y llega a 0.97 (dentro de 0.01 del plateau) en t = 50*ln(90) ~ 225
    assert 150 <= onset.t_onset <= 350


def test_noisy_stationary_series_is_accepted_early():
    """Alto ruido: va fluctua alrededor de un valor desde t=0. No hay
    transitorio que esperar y la corrida NO se descarta."""
    rng = np.random.default_rng(0)
    t = np.arange(0, 2001)
    y = rng.normal(0.5, 0.2, size=t.size)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert onset.t_onset <= 100


def test_large_stationary_fluctuations_are_accepted():
    """Cerca de la transicion va fluctua fuerte pero no deriva: hay que aceptarla.

    Es el pico de susceptibilidad; un criterio que exija tramos de ancho fijo
    chico rechaza justo la region que mas interesa.
    """
    t = np.arange(0, 5001)
    y = 0.43 + 0.15 * np.sin(2 * np.pi * t / 137.0)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert onset.t_onset <= 150


def test_transient_dips_inside_the_stationary_state_do_not_delay_onset():
    """Vicsek rho=2 eta=2: plateau ~0.8 con caidas breves (la bandada se rompe y
    se rearma). Las caidas son parte del estacionario, no un transitorio."""
    t = np.arange(0, 2001)
    y = np.where(t < 100, 0.1, 0.8)
    y[(t >= 600) & (t < 650)] = 0.3
    y[(t >= 1500) & (t < 1550)] = 0.3
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert 80 <= onset.t_onset <= 130


def test_series_still_drifting_at_the_end_is_flagged_but_measured():
    t = np.arange(0, 2001)
    y = 0.2 + 0.6 * t / t[-1]
    onset = detect_onset(t, y, Detector())
    assert onset.status == "drift"
    assert onset.t_onset is not None


def test_too_short():
    t = np.arange(5)
    y = np.ones(5)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "too_short"
    assert onset.t_onset is None


def test_constant_series_starts_at_zero():
    t = np.arange(0, 500)
    y = np.ones(t.size)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert onset.t_onset == 0


def test_t_min_is_a_floor_for_the_onset():
    t = np.arange(0, 500)
    y = np.full(t.size, 0.8)
    onset = detect_onset(t, y, Detector(t_min=100))
    assert onset.status == "ok"
    assert onset.t_onset == 100


def test_onset_follows_the_plateau_not_t_min():
    t = np.arange(0, 501)
    early = np.where(t < 70, 0.15, 0.92)
    late = np.where(t < 220, 0.15, 0.92)
    e = detect_onset(t, early, Detector())
    l = detect_onset(t, late, Detector())
    assert e.status == "ok"
    assert l.status == "ok"
    assert 70 <= e.t_onset <= 100
    assert 220 <= l.t_onset <= 250


def test_dual_onset_independent():
    frame = _series()
    det = Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3)
    rec = detect_run(frame, det)
    assert rec["status_va"] == "ok"
    assert rec["status_S"] == "ok"
    assert rec["t_onset_va"] < rec["t_onset_S"]
    va_ss, _va_std = steady_mean(frame["t"].to_numpy(), frame["va"].to_numpy(), rec["t_onset_va"])
    s_ss, _s_std = steady_mean(frame["t"].to_numpy(), frame["S"].to_numpy(), rec["t_onset_S"])
    assert va_ss > 0.85
    assert s_ss > 0.8


def test_steady_mean_temporal_std_on_plateau():
    t = np.arange(0, 8)
    y = np.array([0.1, 0.1, 0.2, 0.9, 1.1, 0.8, 1.0, 0.7])
    t_onset = 3
    mean, temporal_std = steady_mean(t, y, t_onset)
    tail = y[t >= t_onset]
    assert mean == pytest.approx(float(np.mean(tail)))
    assert temporal_std == pytest.approx(float(np.std(tail, ddof=1)))


def test_ensemble_detects_t0_per_run_and_never_forces_by_model():
    index = pd.DataFrame(
        [
            {**_index_row("vicsek-500"), "model": "vicsek", "T": 500},
            {**_index_row("votante-500"), "model": "votante", "T": 500},
            {**_index_row("votante-5000"), "model": "votante", "T": 5000},
        ]
    )
    serie = _series(t_end=5000)

    def load(_row):
        return serie

    det = Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3)
    onset, _agg = ensemble(index, load, det)

    assert set(onset["status_va"]) == {"ok"}
    assert onset["t_onset_va"].nunique() == 1
    assert onset.iloc[0]["t_onset_va"] == detect_run(serie, det)["t_onset_va"]


def test_explicit_t_onset_still_overrides_the_detector():
    index = pd.DataFrame([_index_row("r1")])

    def load(_row):
        return _series()

    det = Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3)
    onset, _agg = ensemble(index, load, det, t_onset=123)
    assert onset.iloc[0]["t_onset_va"] == 123
    assert onset.iloc[0]["status_va"] == "forced"


def test_ensemble_n1_no_std():
    index = pd.DataFrame([_index_row("r1")])
    frame = _series()

    def load(_row):
        return frame

    _onset, agg = ensemble(index, load, Detector(window=20, atol=0.02, rtol=0.05, t_min=10, sustain=3))
    assert int(agg.iloc[0]["n_runs_va"]) == 1
    assert np.isnan(agg.iloc[0]["va_ss_std"])
    assert np.isfinite(agg.iloc[0]["va_ss_err"])


def test_ensemble_keeps_drifting_runs_and_counts_them():
    t = np.arange(0, 2001)
    frames = {
        "flat": pd.DataFrame({"t": t, "va": np.full(t.size, 0.5), "S": np.full(t.size, 0.5)}),
        "ramp": pd.DataFrame({"t": t, "va": 0.2 + 0.6 * t / t[-1], "S": np.full(t.size, 0.5)}),
    }
    rows = [_index_row("flat", seed=1), _index_row("ramp", seed=2)]

    def load(row):
        return frames[row["run_dir"]]

    onset, agg = ensemble(pd.DataFrame(rows), load, Detector())
    assert int(agg.iloc[0]["n_runs_va"]) == 2
    assert int(agg.iloc[0]["n_drift_va"]) == 1
    assert np.isfinite(agg.iloc[0]["va_ss"])
    report = onset_report(onset)
    assert any("derivando" in line for line in report)


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

