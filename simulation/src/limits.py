"""Shared S-axis limits from the data, not a hardcoded zoom."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FamilyLimits:
    lo: float
    hi: float
    raw_lo: float
    raw_hi: float
    lo_source: str
    hi_source: str
    n_min: int

    @property
    def lims(self) -> tuple[float, float]:
        return (self.lo, self.hi)

    def describe(self, name: str) -> str:
        return (
            f"{name} = [{self.lo:.6g}, {self.hi:.6g}], "
            f"mínimo de {self.lo_source}, máximo de {self.hi_source}"
        )


def _pad_limits(lo: float, hi: float, n_min: int, *, cap_at_one: bool = True) -> tuple[float, float]:
    if n_min <= 0:
        raise ValueError("n_min must be > 0")
    span = hi - lo
    pad = 0.05 * span
    lims = (lo - pad, hi + pad)
    if (lims[1] - lims[0]) < 10.0 / n_min:
        centro = (lo + hi) / 2.0
        half = 5.0 / n_min
        lims = (centro - half, centro + half)
    hi_lim = min(lims[1], 1.0 + pad) if cap_at_one else lims[1]
    return (lims[0], hi_lim)


def family_limits(
    samples: list[tuple[float, str]],
    n_min: int,
) -> FamilyLimits:
    finite = [(float(value), source) for value, source in samples if np.isfinite(value)]
    if not finite:
        raise ValueError("family_limits needs at least one finite sample")
    lo_value, lo_source = min(finite, key=lambda item: item[0])
    hi_value, hi_source = max(finite, key=lambda item: item[0])
    lo, hi = _pad_limits(lo_value, hi_value, n_min)
    return FamilyLimits(
        lo=lo,
        hi=hi,
        raw_lo=lo_value,
        raw_hi=hi_value,
        lo_source=lo_source,
        hi_source=hi_source,
        n_min=n_min,
    )


def cover(limits: FamilyLimits, values: np.ndarray) -> FamilyLimits:
    """Widen limits so every finite value fits. The 1+pad cap does not apply here."""
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return limits
    vmin = float(np.min(finite))
    vmax = float(np.max(finite))
    if vmin >= limits.lo and vmax <= limits.hi:
        return limits
    lo_value = min(limits.raw_lo, vmin)
    hi_value = max(limits.raw_hi, vmax)
    lo_source = limits.lo_source if lo_value == limits.raw_lo else "clip-check expand"
    hi_source = limits.hi_source if hi_value == limits.raw_hi else "clip-check expand"
    lo, hi = _pad_limits(lo_value, hi_value, limits.n_min, cap_at_one=False)
    if vmin < lo or vmax > hi:
        extra = max(0.05 * max(hi - lo, vmax - vmin), 0.5 / limits.n_min)
        lo = min(lo, vmin) - extra
        hi = max(hi, vmax) + extra
    return replace(
        limits,
        lo=lo,
        hi=hi,
        raw_lo=lo_value,
        raw_hi=hi_value,
        lo_source=lo_source,
        hi_source=hi_source,
    )


def temporal_samples(index: pd.DataFrame, load_series) -> list[tuple[float, str]]:
    samples: list[tuple[float, str]] = []
    for _, row in index.iterrows():
        data = load_series(row)
        model = str(row["model"])
        rho = float(row["rho"])
        eta = float(row["eta"])
        for t, s in zip(data["t"].to_numpy(), data["S"].to_numpy()):
            samples.append(
                (float(s), f"{_model_name(model)} ρ={rho:g} η={eta:g} en t={int(t)}")
            )
    return samples


def stationary_samples(agg: pd.DataFrame, err_col: str = "S_ss_std") -> list[tuple[float, str]]:
    samples: list[tuple[float, str]] = []
    err_name = err_col if err_col in agg.columns else "S_ss_err"
    for _, row in agg.iterrows():
        mean = float(row["S_ss"])
        err = float(row[err_name]) if err_name in row and np.isfinite(row[err_name]) else 0.0
        model = _model_name(row["model"])
        rho = float(row["rho"])
        eta = float(row["eta"])
        label = f"{model} ρ={rho:g} η={eta:g}"
        samples.append((mean, f"{label} ⟨S⟩"))
        samples.append((mean - err, f"{label} ⟨S⟩−σ"))
        samples.append((mean + err, f"{label} ⟨S⟩+σ"))
    return samples


def n_min_from(frame: pd.DataFrame, *, default_l: int = 10) -> int:
    if frame.empty:
        return default_l * default_l * 2
    if "N" in frame.columns and frame["N"].notna().any():
        return int(frame["N"].min())
    rhos = frame["rho"].astype(float)
    l_col = frame["L"].astype(float) if "L" in frame.columns else default_l
    return int(np.min(np.round(rhos * l_col * l_col)))


def _model_name(model) -> str:
    return "Vicsek" if str(model) == "vicsek" else "Votante"


def compute_s_limits(index: pd.DataFrame, agg: pd.DataFrame, load_series) -> tuple[FamilyLimits, FamilyLimits]:
    temporal = family_limits(temporal_samples(index, load_series), n_min_from(index if not index.empty else agg))
    stationary = family_limits(stationary_samples(agg), n_min_from(agg if not agg.empty else index))
    return temporal, stationary
