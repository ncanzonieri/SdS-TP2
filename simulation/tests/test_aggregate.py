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


def test_sustain_adds_real_evidence():
    """Cola en V: las dos mitades coinciden, los cuatro cuartos no.

    Con ventanas corridas y solapadas `sustain` no distinguia estos dos casos.
    """
    t = np.arange(0, 400)
    y = np.concatenate(
        [np.full(100, 0.5), np.full(100, 0.3), np.full(100, 0.3), np.full(100, 0.5)]
    )
    assert detect_onset(t, y, _d(100, 0.02, 0.05, 0, 1)).status == "ok"
    assert detect_onset(t, y, _d(100, 0.02, 0.05, 0, 3)).status == "never"


def test_wandering_series_is_not_stationary():
    """Regresion: la forma de votante eta=0 truncado a T=500.

    va deambula (0.38 -> 0.53 -> 0.39) sin haber llegado al estacionario; el
    valor real de la corrida larga es 1.0. El criterio de ventanas corridas la
    aceptaba con t0=207 y estimaba 0.52.
    """
    t = np.arange(0, 501)
    y = np.concatenate(
        [
            np.full(100, 0.20),
            np.full(100, 0.38),
            np.full(100, 0.53),
            np.full(100, 0.45),
            np.full(101, 0.39),
        ]
    )
    assert detect_onset(t, y, Detector()).status == "never"


def test_large_stationary_fluctuations_are_accepted():
    """Cerca de la transicion va fluctua fuerte pero no deriva: hay que aceptarla.

    Es el pico de susceptibilidad; un criterio que exija tramos de ancho fijo
    chico rechaza justo la region que mas interesa.
    """
    t = np.arange(0, 5001)
    y = 0.43 + 0.15 * np.sin(2 * np.pi * t / 137.0)
    onset = detect_onset(t, y, Detector())
    assert onset.status == "ok"
    assert onset.t_onset == 100


def test_tail_shorter_than_required_is_too_short():
    det = Detector()
    assert det.min_tail == 400
    # Corrida larga: se conserva el window configurado.
    assert det.required_tail(9900) == 400
    # T=500 (n=401 tras t_min=100): achica la cola para poder barrer t0.
    assert 240 <= det.required_tail(401) < 400
    t = np.arange(0, 150)
    y = np.full(t.size, 0.8)
    assert detect_onset(t, y, det).status == "too_short"


def test_t500_onset_follows_the_plateau_not_t_min():
    """Con T=500 el min_tail=400 dejaba un solo candidato: t=100.

    La linea de (b) quedaba bien si el plateau empezaba antes, y mal si la
    serie todavia subia. t0 tiene que correrse con esa curva.
    """
    t = np.arange(0, 501)
    early = np.where(t < 70, 0.15, 0.92)
    late = np.where(t < 220, 0.15, 0.92)
    e = detect_onset(t, early, Detector())
    l = detect_onset(t, late, Detector())
    assert e.status == "ok"
    assert l.status == "ok"
    assert e.t_onset == 100
    assert 200 <= l.t_onset <= 240
    assert l.t_onset > e.t_onset


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


def test_ensemble_detects_t0_per_run_and_never_forces_by_model():
    """t0 lo decide el detector corrida por corrida.

    Antes habia una constante por modelo (200 Vicsek / 2500 votante) que se
    aplicaba segun el largo declarado de la corrida, asi que dos modelos en la
    misma figura terminaban con criterios distintos.
    """
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
    # Misma serie: mismo t0, sin importar el modelo ni el T declarado.
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
