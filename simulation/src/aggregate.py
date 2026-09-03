"""Steady-state onset (per observable) and ensemble means.

Criterio del estacionario (punto b del enunciado)
-------------------------------------------------
Para cada corrida y cada observable `y(t)` (va o S):

1. Se suaviza la serie con un promedio movil centrado de ancho `window`.
2. La ultima fraccion `tail_frac` de la corrida define la *banda estacionaria*:
   el rango entre los percentiles `quantile` y `1 - quantile` del promedio
   movil en esa cola, ensanchado por `max(atol, rtol * ancho)`. La banda
   captura la amplitud natural de las fluctuaciones del estacionario, asi que
   cerca de la transicion (fluctuaciones grandes) la banda es ancha y lejos
   (plateau) es angosta.
3. `t0` es el primer instante a partir del cual el promedio movil entra en la
   banda, permanece dentro al menos `sustain` pasos seguidos y desde ahi hasta
   el final queda fuera de la banda a lo sumo una fraccion `max_outside` del
   tiempo. Es decir: el transitorio termina cuando la serie ya fluctua como lo
   hace en la cola.
4. La cola se revisa por deriva: si las medias de sus dos mitades difieren en
   mas de `max(2*atol, drift_tol * ancho_banda)` la serie sigue evolucionando
   en t=T. El promedio se calcula igual (desde t0) pero la corrida queda
   marcada `drift` para avisarlo en la consola y en las tablas.

El valor escalar de cada corrida es el promedio temporal de `y` en `[t0, T]`;
el valor del punto (modelo, rho, eta) es la media de esos promedios sobre las
semillas, con su desvio estandar como barra de error.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

STATUS_OK = "ok"
STATUS_DRIFT = "drift"
STATUS_FORCED = "forced"
STATUS_SHORT = "too_short"
USABLE = {STATUS_OK, STATUS_DRIFT, STATUS_FORCED}


@dataclass(frozen=True)
class Onset:
    t_onset: int | None
    status: str
    band_lo: float = float("nan")
    band_hi: float = float("nan")


@dataclass
class Detector:
    window: int = 50
    atol: float = 0.01
    rtol: float = 0.10
    t_min: int = 0
    sustain: int = 100
    tail_frac: float = 0.5
    quantile: float = 0.025
    max_outside: float = 0.10
    drift_tol: float = 0.25
    min_points: int = 10

    def effective_window(self, n: int) -> int:
        """Ancho del promedio movil acotado por el largo de la serie."""
        return max(1, min(self.window, n // 10))

    def validate(self) -> None:
        if self.window <= 0:
            raise ValueError("window must be > 0")
        if self.sustain <= 0:
            raise ValueError("sustain must be > 0")
        if not 0.0 < self.tail_frac < 1.0:
            raise ValueError("tail_frac must be in (0, 1)")
        if not 0.0 <= self.quantile < 0.5:
            raise ValueError("quantile must be in [0, 0.5)")
        if not 0.0 <= self.max_outside < 1.0:
            raise ValueError("max_outside must be in [0, 1)")


def moving_average(y: np.ndarray, w: int) -> np.ndarray:
    """Promedio movil de ancho w; el elemento i cubre y[i : i + w]."""
    y = np.asarray(y, dtype=float)
    if w <= 1:
        return y.copy()
    cumsum = np.concatenate(([0.0], np.cumsum(y)))
    return (cumsum[w:] - cumsum[:-w]) / w


def stationary_band(tail_ma: np.ndarray, detector: Detector) -> tuple[float, float]:
    lo = float(np.quantile(tail_ma, detector.quantile))
    hi = float(np.quantile(tail_ma, 1.0 - detector.quantile))
    margin = max(detector.atol, detector.rtol * (hi - lo))
    return lo - margin, hi + margin


def _run_lengths_ahead(inside: np.ndarray) -> np.ndarray:
    """run[i] = cantidad de True consecutivos empezando en i."""
    run = np.zeros(inside.size, dtype=int)
    count = 0
    for i in range(inside.size - 1, -1, -1):
        count = count + 1 if inside[i] else 0
        run[i] = count
    return run


def detect_onset(t: np.ndarray, y: np.ndarray, detector: Detector) -> Onset:
    detector.validate()
    t = np.asarray(t, dtype=int)
    y = np.asarray(y, dtype=float)
    if t.size != y.size:
        raise ValueError("t and y must have the same length")

    order = np.argsort(t, kind="stable")
    t_s = t[order]
    y_s = y[order]
    mask = t_s >= detector.t_min
    t_s = t_s[mask]
    y_s = y_s[mask]

    n = int(y_s.size)
    if n < max(detector.min_points, 4):
        return Onset(None, STATUS_SHORT)

    w = detector.effective_window(n)
    ma = moving_average(y_s, w)
    m = int(ma.size)
    centers = np.arange(m) + w // 2

    tail_i0 = int(np.floor(m * (1.0 - detector.tail_frac)))
    tail_i0 = min(max(tail_i0, 0), m - 1)
    tail_ma = ma[tail_i0:]
    lo, hi = stationary_band(tail_ma, detector)
    inside = (ma >= lo) & (ma <= hi)

    sustain = max(1, min(detector.sustain, m - tail_i0))
    run_ahead = _run_lengths_ahead(inside)
    outside_suffix = np.cumsum((~inside)[::-1])[::-1]
    remaining = m - np.arange(m)
    outside_frac = outside_suffix / remaining

    candidates = np.flatnonzero((run_ahead >= sustain) & (outside_frac <= detector.max_outside))
    if candidates.size:
        i = int(candidates[0])
    else:
        # La cola define la banda, asi que casi siempre hay candidato. Si no lo
        # hay (cola muy irregular) se promedia la cola entera.
        i = tail_i0
    t0 = int(t_s[0]) if i == 0 else int(t_s[min(centers[i], n - 1)])

    # Deriva: la cola sigue moviendose en t=T.
    tail_y = y_s[n - max(2, int(np.floor(n * detector.tail_frac))):]
    half = tail_y.size // 2
    drift = abs(float(np.mean(tail_y[:half])) - float(np.mean(tail_y[half:])))
    threshold = max(2.0 * detector.atol, detector.drift_tol * (hi - lo))
    status = STATUS_DRIFT if drift > threshold else STATUS_OK
    return Onset(t0, status, lo, hi)


def detect_run(
    observables: pd.DataFrame,
    detector: Detector,
    *,
    force_va: int | None = None,
    force_s: int | None = None,
) -> dict:
    t = observables["t"].to_numpy()
    va = detect_onset(t, observables["va"].to_numpy(), detector)
    s = detect_onset(t, observables["S"].to_numpy(), detector)
    if force_va is not None:
        va = Onset(int(force_va), STATUS_FORCED, va.band_lo, va.band_hi)
    if force_s is not None:
        s = Onset(int(force_s), STATUS_FORCED, s.band_lo, s.band_hi)
    return {
        "t_onset_va": va.t_onset,
        "status_va": va.status,
        "band_lo_va": va.band_lo,
        "band_hi_va": va.band_hi,
        "t_onset_S": s.t_onset,
        "status_S": s.status,
        "band_lo_S": s.band_lo,
        "band_hi_S": s.band_hi,
    }


def steady_mean(t: np.ndarray, y: np.ndarray, t_onset: int | None) -> tuple[float, float]:
    if t_onset is None:
        return float("nan"), float("nan")
    t = np.asarray(t)
    y = np.asarray(y, dtype=float)
    tail = y[t >= t_onset]
    if tail.size == 0:
        return float("nan"), float("nan")
    mean = float(np.mean(tail))
    temporal_std = float(np.std(tail, ddof=1)) if tail.size > 1 else 0.0
    return mean, temporal_std


def _force_map(csv_path: str | None, global_t: int | None) -> dict[str, tuple[int | None, int | None]]:
    mapping: dict[str, tuple[int | None, int | None]] = {}
    if global_t is not None:
        mapping["*"] = (global_t, global_t)
    if not csv_path:
        return mapping
    frame = pd.read_csv(csv_path)
    if "run_dir" not in frame.columns:
        raise ValueError("t-onset csv needs a run_dir column")
    has_dual = "t_onset_va" in frame.columns and "t_onset_S" in frame.columns
    has_single = "t_onset" in frame.columns
    if not has_dual and not has_single:
        raise ValueError("t-onset csv needs t_onset or both t_onset_va and t_onset_S")
    for _, row in frame.iterrows():
        key = str(row["run_dir"])
        if has_dual:
            mapping[key] = (int(row["t_onset_va"]), int(row["t_onset_S"]))
        else:
            forced = int(row["t_onset"])
            mapping[key] = (forced, forced)
    return mapping


def ensemble(
    index: pd.DataFrame,
    load_series,
    detector: Detector,
    *,
    t_onset: int | None = None,
    t_onset_csv: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Onset por corrida + promedios por (modelo, rho, eta)."""
    forces = _force_map(t_onset_csv, t_onset)
    onset_rows: list[dict] = []
    ss_rows: list[dict] = []
    for _, row in index.iterrows():
        series = load_series(row)
        key = str(row["run_dir"])
        # Sin override explicito decide el detector, corrida por corrida: t0 es
        # donde ESA serie se vuelve estacionaria, no una constante por modelo.
        forced = forces.get(key, forces.get("*", (None, None)))
        detected = detect_run(series, detector, force_va=forced[0], force_s=forced[1])
        onset_rows.append({**row.to_dict(), **detected})
        if detected["status_va"] in USABLE:
            va_ss, va_ss_temporal = steady_mean(
                series["t"].to_numpy(), series["va"].to_numpy(), detected["t_onset_va"]
            )
        else:
            va_ss, va_ss_temporal = float("nan"), float("nan")
        if detected["status_S"] in USABLE:
            s_ss, s_ss_temporal = steady_mean(
                series["t"].to_numpy(), series["S"].to_numpy(), detected["t_onset_S"]
            )
        else:
            s_ss, s_ss_temporal = float("nan"), float("nan")
        ss_rows.append(
            {
                "model": row["model"],
                "rho": float(row["rho"]),
                "eta": float(row["eta"]),
                "run_dir": row["run_dir"],
                "va_ss": va_ss,
                "S_ss": s_ss,
                "va_ss_temporal": va_ss_temporal,
                "S_ss_temporal": s_ss_temporal,
                **detected,
            }
        )
    onset = pd.DataFrame(onset_rows)
    per_run = pd.DataFrame(ss_rows)
    grouped = []
    for keys, chunk in per_run.groupby(["model", "rho", "eta"], sort=True):
        model, rho, eta = keys
        va = chunk["va_ss"].dropna()
        s = chunk["S_ss"].dropna()
        va_err = chunk["va_ss_temporal"].dropna()
        s_err = chunk["S_ss_temporal"].dropna()
        n_va, n_s = int(va.size), int(s.size)
        n_va_err, n_s_err = int(va_err.size), int(s_err.size)
        grouped.append(
            {
                "model": model,
                "rho": float(rho),
                "eta": float(eta),
                "n_runs_va": n_va,
                "n_runs_S": n_s,
                "n_drift_va": int((chunk["status_va"] == STATUS_DRIFT).sum()),
                "n_drift_S": int((chunk["status_S"] == STATUS_DRIFT).sum()),
                "t_onset_va_median": chunk.loc[chunk["status_va"].isin(USABLE), "t_onset_va"].median(),
                "t_onset_S_median": chunk.loc[chunk["status_S"].isin(USABLE), "t_onset_S"].median(),
                "va_ss": float(va.mean()) if n_va else float("nan"),
                "va_ss_std": float(va.std(ddof=1)) if n_va > 1 else float("nan"),
                "va_ss_err": float(va_err.mean()) if n_va_err else float("nan"),
                "S_ss": float(s.mean()) if n_s else float("nan"),
                "S_ss_std": float(s.std(ddof=1)) if n_s > 1 else float("nan"),
                "S_ss_err": float(s_err.mean()) if n_s_err else float("nan"),
            }
        )
    agg = pd.DataFrame(grouped)
    return onset, agg


def onset_report(onset: pd.DataFrame) -> list[str]:
    """Lineas de aviso: corridas que no alcanzaron un estacionario limpio."""
    messages: list[str] = []
    if onset.empty:
        return messages
    for col, label in (("status_va", "va"), ("status_S", "S")):
        if col not in onset.columns:
            continue
        short = onset.loc[onset[col] == STATUS_SHORT]
        drift = onset.loc[onset[col] == STATUS_DRIFT]
        if not short.empty:
            messages.append(
                f"{label}: {len(short)} corridas demasiado cortas para detectar el estacionario "
                f"(sin valor): {', '.join(short['run_dir'].astype(str).head(5))}"
                + (" ..." if len(short) > 5 else "")
            )
        if not drift.empty:
            groups = (
                drift.groupby(["model", "rho", "eta"], sort=True)["run_dir"]
                .size()
                .reset_index(name="n")
            )
            described = ", ".join(
                f"{row['model']} ρ={float(row['rho']):g} η={float(row['eta']):g} ({int(row['n'])})"
                for _, row in groups.iterrows()
            )
            messages.append(
                f"{label}: {len(drift)} corridas siguen derivando en t=T (se promedian igual desde t0, "
                f"conviene alargar T): {described}"
            )
    return messages


def warn_ranges(series: pd.DataFrame) -> list[str]:
    messages: list[str] = []
    if (series["va"] < 0).any() or (series["va"] > 1).any():
        messages.append("va outside [0, 1]")
    if (series["S"] <= 0).any() or (series["S"] > 1).any():
        messages.append("S outside (0, 1]")
    return messages
