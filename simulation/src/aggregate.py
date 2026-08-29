"""Steady-state onset (per observable) and ensemble means."""

from __future__ import annotations

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


def detect_onset(t: np.ndarray, y: np.ndarray, detector: Detector, *, eps: float = 1e-12) -> Onset:
    t = np.asarray(t, dtype=int)
    y = np.asarray(y, dtype=float)
    if t.size != y.size:
        raise ValueError("t and y must have the same length")
    if detector.window <= 0 or detector.sustain <= 0:
        raise ValueError("window and sustain must be > 0")

    order = np.argsort(t)
    t = t[order]
    y = y[order]
    mask = t >= detector.t_min
    t_s = t[mask]
    y_s = y[mask]
    if t_s.size < 2 * detector.window:
        return Onset(None, STATUS_SHORT)

    last = t_s.size - 2 * detector.window
    if last < 0:
        return Onset(None, STATUS_SHORT)

    streak = 0
    streak_start: int | None = None
    for i in range(0, last + 1):
        m1 = float(np.mean(y_s[i : i + detector.window]))
        m2 = float(np.mean(y_s[i + detector.window : i + 2 * detector.window]))
        tol = detector.atol + detector.rtol * max(abs(m2), eps)
        if abs(m1 - m2) <= tol:
            if streak == 0:
                streak_start = int(t_s[i])
            streak += 1
            if streak >= detector.sustain:
                return Onset(streak_start, STATUS_OK)
        else:
            streak = 0
            streak_start = None
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


def steady_mean(t: np.ndarray, y: np.ndarray, t_onset: int | None) -> float:
    if t_onset is None:
        return float("nan")
    t = np.asarray(t)
    y = np.asarray(y, dtype=float)
    tail = y[t >= t_onset]
    if tail.size == 0:
        return float("nan")
    return float(np.mean(tail))


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
        forced = forces.get(key, forces.get("*", (None, None)))
        detected = detect_run(series, detector, force_va=forced[0], force_s=forced[1])
        onset_rows.append({**row.to_dict(), **detected})
        va_ss = (
            steady_mean(series["t"].to_numpy(), series["va"].to_numpy(), detected["t_onset_va"])
            if detected["status_va"] in USABLE
            else float("nan")
        )
        s_ss = (
            steady_mean(series["t"].to_numpy(), series["S"].to_numpy(), detected["t_onset_S"])
            if detected["status_S"] in USABLE
            else float("nan")
        )
        ss_rows.append(
            {
                "model": row["model"],
                "rho": float(row["rho"]),
                "eta": float(row["eta"]),
                "run_dir": row["run_dir"],
                "va_ss": va_ss,
                "S_ss": s_ss,
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
        n_va, n_s = int(va.size), int(s.size)
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
                "S_ss": float(s.mean()) if n_s else float("nan"),
                "S_ss_std": float(s.std(ddof=1)) if n_s > 1 else float("nan"),
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
