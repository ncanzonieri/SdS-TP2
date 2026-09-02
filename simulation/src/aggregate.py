"""Steady-state onset (per observable) and ensemble means."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

STATUS_OK = "ok"
STATUS_NEVER = "never"
STATUS_FORCED = "forced"
STATUS_SHORT = "too_short"
USABLE = {STATUS_OK, STATUS_FORCED}


@dataclass(frozen=True)
class Onset:
    t_onset: int | None
    status: str


@dataclass
class Detector:
    window: int = 100
    atol: float = 0.02
    rtol: float = 0.05
    t_min: int = 100
    sustain: int = 3
    tail_frac: float = 0.6
    min_segment: int = 20

    @property
    def segments(self) -> int:
        """En cuantos tramos iguales se parte la cola para validarla."""
        return self.sustain + 1

    @property
    def min_tail(self) -> int:
        return self.segments * self.window

    def required_tail(self, n: int) -> int:
        """Confirmation length after a candidate t0: min(window tail, frac of n)."""
        floor = self.segments * self.min_segment
        if n <= 0:
            return max(self.min_tail, floor)
        return min(self.min_tail, max(floor, math.ceil(self.tail_frac * n)))


def detect_onset(t: np.ndarray, y: np.ndarray, detector: Detector, *, eps: float = 1e-12) -> Onset:
    t = np.asarray(t, dtype=int)
    y = np.asarray(y, dtype=float)
    if t.size != y.size:
        raise ValueError("t and y must have the same length")
    if detector.window <= 0 or detector.sustain <= 0:
        raise ValueError("window and sustain must be > 0")

    order = np.argsort(t)
    t_s = t[order]
    y_s = y[order]
    mask = t_s >= detector.t_min
    t_s = t_s[mask]
    y_s = y_s[mask]

    size = y_s.size
    need = detector.required_tail(size)
    if size < need:
        return Onset(None, STATUS_SHORT)

    n_seg = detector.segments
    # cumsum[k] = suma de y_s[:k]; da la media de cualquier tramo en O(1).
    # Como lista de floats de Python: el escaneo hace aritmetica escalar, no vectorial.
    cumsum = np.concatenate(([0.0], np.cumsum(y_s))).tolist()

    for i in range(0, size - need + 1):
        seg = (size - i) // n_seg
        end = i + n_seg * seg
        ref = (cumsum[end] - cumsum[i]) / (end - i)
        tol = detector.atol + detector.rtol * max(abs(ref), eps)
        if all(
            abs((cumsum[a + seg] - cumsum[a]) / seg - ref) <= tol
            for a in range(i, end, seg)
        ):
            return Onset(int(t_s[i]), STATUS_OK)
    return Onset(None, STATUS_NEVER)


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
        va = Onset(int(force_va), STATUS_FORCED)
    if force_s is not None:
        s = Onset(int(force_s), STATUS_FORCED)
    return {
        "t_onset_va": va.t_onset,
        "status_va": va.status,
        "t_onset_S": s.t_onset,
        "status_S": s.status,
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


def warn_ranges(series: pd.DataFrame) -> list[str]:
    messages: list[str] = []
    if (series["va"] < 0).any() or (series["va"] > 1).any():
        messages.append("va outside [0, 1]")
    if (series["S"] <= 0).any() or (series["S"] > 1).any():
        messages.append("S outside (0, 1]")
    return messages
