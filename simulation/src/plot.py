"""Matplotlib figures b–g and a Plotly HTML explorer."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from matplotlib.lines import Line2D

from src.aggregate import USABLE
from src.io import read_tp1_csv, rho_close
from src.limits import FamilyLimits, cover, family_limits, n_min_from, stationary_samples, temporal_samples
from src.paths import ensure_dir

GENERAL_RHOS = (2.0, 4.0, 8.0)
# Densidades bajas del estudio de clusters: 1/(3pi), 1/(2pi), 1/pi. Con rc=1 las
# tres del enunciado dan S~1 constante (el grafo de vecindad esta muy por encima
# de percolacion), asi que S solo informa aca abajo. Java nombra las carpetas con
# rho = N/L^2 (0.11 / 0.16 / 0.32); `rho_close` puentea ambas escrituras.
LOW_RHOS = (0.1061, 0.1592, 0.3183)
CLUSTER_RHOS = LOW_RHOS + GENERAL_RHOS
CHARACTERISTIC_ETAS = (0, 1.5, 3.0)
FIG_CHOICES = ("png", "pdf", "both", "none")
_FIG_FORMATS: frozenset[str] = frozenset({"png"})

CURVE_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
RHO_COLORS = {
    0.11: "#8c564b",
    0.16: "#9467bd",
    0.32: "#e377c2",
    2.0: "#1f77b4",
    4.0: "#ff7f0e",
    8.0: "#2ca02c",
}
MODEL_LINE = {"vicsek": "-", "votante": "--"}
RHO_MARKER = {
    0.1061: "v",
    0.1592: "D",
    0.3183: "s",
    2.0: "o",
    4.0: "^",
    8.0: "P",
}
VA_YLIM = (0.0, 1.02)


def parse_fig_formats(spec: str) -> frozenset[str]:
    if spec not in FIG_CHOICES:
        raise ValueError(f"invalid --figs {spec!r}; expected {', '.join(FIG_CHOICES)}")
    if spec == "both":
        return frozenset({"png", "pdf"})
    if spec == "none":
        return frozenset()
    return frozenset({spec})


def set_fig_formats(spec: str) -> frozenset[str]:
    global _FIG_FORMATS
    _FIG_FORMATS = parse_fig_formats(spec)
    return _FIG_FORMATS


def fig_formats() -> frozenset[str]:
    return _FIG_FORMATS


def apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 200,
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.axisbelow": True,
            "legend.frameon": True,
            "lines.linewidth": 1.5,
            "lines.markersize": 5,
        }
    )


def _strip_titles(fig: plt.Figure) -> None:
    """GuiaPresentaciones 1.7 / README: figures carry no in-plot title."""
    sup = getattr(fig, "_suptitle", None)
    if sup is not None:
        sup.set_text("")
    for ax in fig.axes:
        ax.set_title("")


LEGEND_MAX_INSIDE = 6


def place_legend(ax, handles=None, labels=None, *, max_inside: int = LEGEND_MAX_INSIDE, **kwargs) -> None:
    """Leyenda adentro si es corta; afuera (derecha) si taparia las curvas."""
    if handles is None or labels is None:
        handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return
    kwargs = dict(kwargs)
    if len(handles) > max_inside:
        kwargs.pop("ncols", None)
        kwargs.update(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0)
    else:
        kwargs.setdefault("loc", "best")
    ax.legend(handles, labels, **kwargs)


def save(fig: plt.Figure, stem: Path) -> None:
    ensure_dir(stem.parent)
    _strip_titles(fig)
    formats = fig_formats()
    for ext in sorted(formats):
        fig.savefig(stem.parent / f"{stem.name}.{ext}", bbox_inches="tight")
    plt.close(fig)


def save_curve_panel(
    stem: Path,
    painter,
    *,
    figsize: tuple[float, float],
    xlabel: str,
    ylabel: str,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    legend_kwargs: dict | None = None,
    clip_s: FamilyLimits | None = None,
    clip_axis: str = "y",
) -> Path:
    apply_style()
    fig, ax = plt.subplots(figsize=figsize)
    painter(ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if clip_s is not None:
        _apply_s_clip(ax, clip_s, axis=clip_axis)
    place_legend(ax, **(legend_kwargs or {}))
    save(fig, stem)
    return stem


def _color(i: int) -> str:
    return CURVE_COLORS[i % len(CURVE_COLORS)]


def _rho_color(rho: float) -> str:
    for key, color in RHO_COLORS.items():
        if rho_close(rho, key):
            return color
    return _color(0)


def _marker(rho: float) -> str:
    for key, mark in RHO_MARKER.items():
        if rho_close(rho, key):
            return mark
    return "o"


def _line(model: str) -> str:
    return MODEL_LINE.get(str(model), "-")


def _is_vicsek(model) -> bool:
    return str(model) == "vicsek"


def _fill_kwargs(model, color: str) -> dict:
    if _is_vicsek(model):
        return {"markerfacecolor": color, "markeredgecolor": color}
    return {"markerfacecolor": "none", "markeredgecolor": color}


def _model_name(model: str) -> str:
    return "Vicsek" if str(model) == "vicsek" else "Votante"


def file_stem(point: str, kind: str, *, model=None, rho=None, eta=None) -> str:
    parts = [point, kind]
    if model is not None:
        parts.append(str(model))
    if rho is not None:
        parts.append(f"rho{float(rho):g}")
    if eta is not None:
        parts.append(f"eta{float(eta):g}")
    return "_".join(parts)


def _yerr_col(frame: pd.DataFrame, prefix: str) -> str:
    std = f"{prefix}_ss_std"
    if std in frame.columns and frame[std].notna().any():
        return std
    return f"{prefix}_ss_err"


def _ax_s_values(ax, axis: str) -> np.ndarray:
    values: list[float] = []
    for line in ax.lines:
        data = line.get_ydata() if axis == "y" else line.get_xdata()
        values.extend(np.ravel(np.asarray(data, dtype=float)))
    for collection in ax.collections:
        offs = collection.get_offsets()
        if len(offs):
            values.extend(np.asarray(offs[:, 1 if axis == "y" else 0], dtype=float))
        get_segments = getattr(collection, "get_segments", None)
        if get_segments is None:
            continue
        for segment in get_segments():
            arr = np.asarray(segment, dtype=float)
            if arr.size == 0:
                continue
            values.extend(arr[:, 1 if axis == "y" else 0])
    return np.asarray(values, dtype=float)


def _apply_s_clip(ax, limits: FamilyLimits, *, axis: str) -> FamilyLimits:
    current = limits
    for _ in range(6):
        values = _ax_s_values(ax, axis)
        widened = cover(current, values)
        if axis == "y":
            ax.set_ylim(widened.lo, widened.hi)
        else:
            ax.set_xlim(widened.lo, widened.hi)
        if widened.lims == current.lims:
            leftover = values[np.isfinite(values)]
            if leftover.size and (leftover.min() < widened.lo or leftover.max() > widened.hi):
                current = cover(widened, leftover)
                continue
            return widened
        current = widened
    raise ValueError(f"S {axis}-axis still clips data after expanding: {current.describe('S')}")


def _stationary_limits(agg: pd.DataFrame, limits: FamilyLimits | None) -> FamilyLimits:
    if limits is not None:
        return limits
    return _local_s_limits(agg)


def _local_s_limits(frame: pd.DataFrame) -> FamilyLimits:
    return family_limits(stationary_samples(frame), n_min_from(frame))


def _temporal_limits(index, load_series, limits: FamilyLimits | None) -> FamilyLimits:
    if limits is not None:
        return limits
    return family_limits(temporal_samples(index, load_series), n_min_from(index))


def _e_xlim(limits: FamilyLimits) -> tuple[float, float]:
    span = max(limits.hi - limits.lo, 1.0 / limits.n_min)
    extra = max(0.08 * span, 1.0 / limits.n_min)
    return (limits.lo, limits.hi + extra)


def filter_rhos(frame: pd.DataFrame, wanted: list[float] | None) -> pd.DataFrame:
    if not wanted:
        return frame
    mask = np.zeros(len(frame), dtype=bool)
    for w in wanted:
        mask |= np.array([rho_close(float(r), w) for r in frame["rho"]])
    return frame.loc[mask].copy()


def warn_missing_rhos(present: list[float], expected: tuple[float, ...], stream=None) -> None:
    stream = stream or sys.stderr
    found = []
    missing = []
    for exp in expected:
        if any(rho_close(p, exp) for p in present):
            found.append(exp)
        else:
            missing.append(exp)
    if missing:
        print(
            f"warning: missing densities {missing}; expected {list(expected)}; found {sorted(set(present))}",
            file=stream,
        )


ONSET_COLUMNS = ("run_dir", "t_onset_va", "status_va", "t_onset_S", "status_S")


def default_rhos(kind: str) -> tuple[float, ...] | None:
    if kind == "c":
        return GENERAL_RHOS
    if kind in {"d", "e"}:
        return CLUSTER_RHOS
    return None


def _onset_cols(onset: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in ONSET_COLUMNS if c not in onset.columns]
    if missing:
        raise KeyError(f"onset table missing columns {missing}")
    return onset.loc[:, list(ONSET_COLUMNS)]


def select_fig_b_runs(index: pd.DataFrame, onset: pd.DataFrame | None = None) -> pd.DataFrame:
    rhos = [float(r) for r in index["rho"].unique()]
    target = 4.0 if any(rho_close(r, 4.0) for r in rhos) else (GENERAL_RHOS[0] if rhos else None)
    if target is None:
        return index
    at_rho = index.loc[index["rho"].map(lambda r: rho_close(float(r), target))]
    if at_rho.empty:
        return index
    etas = sorted(float(e) for e in at_rho["eta"].unique())
    pick = {
        min(etas, key=lambda eta: abs(eta - target))
        for target in CHARACTERISTIC_ETAS
    }
    chosen = at_rho.loc[
        at_rho["eta"].map(lambda eta: any(np.isclose(float(eta), target) for target in pick))
    ]
    if onset is None:
        onset = pd.DataFrame(columns=list(ONSET_COLUMNS))
    status = pd.Series(dtype=object)
    if not onset.empty:
        status = _onset_cols(onset).drop_duplicates("run_dir").set_index("run_dir")["status_va"]
    chosen = chosen.copy()
    chosen["_usable"] = chosen["run_dir"].map(status).isin(USABLE)
    sort_cols = ["_usable", "model", "eta"]
    ascending = [False, True, True]
    for column in ("seed", "run_dir"):
        if column in chosen.columns:
            sort_cols.append(column)
            ascending.append(True)
    chosen = chosen.sort_values(sort_cols, ascending=ascending)
    return chosen.drop(columns=["_usable"]).drop_duplicates(subset=["model", "eta"], keep="first")


def _b_items(frame: pd.DataFrame) -> list[tuple[pd.Series, str]]:
    return [(row, _color(i)) for i, (_, row) in enumerate(frame.iterrows())]


def _plot_b_curve(ax, row, data, col, onset_col, status_col, color, compare) -> None:
    label = (
        f"{_model_name(row['model'])} | "
        f"ρ={row['rho']:g} | η={row['eta']:g} | semilla={row['seed']}"
    )
    t_on = row.get(onset_col)
    status = row.get(status_col)
    if status in USABLE and pd.notna(t_on):
        label += f" | t₀={float(t_on):g}"
    ax.plot(
        data["t"],
        data[col],
        linestyle=_line(row["model"]) if compare else "-",
        color=color,
        alpha=0.9,
        label=label,
    )
    if status in USABLE and pd.notna(t_on):
        ax.axvline(float(t_on), color=color, linestyle="--", linewidth=1.0, alpha=0.75)


def _save_b_figure(stem: Path, wanted: list[str], items, load_series, compare, s_limits=None) -> Path:
    apply_style()
    n_ax = len(wanted)
    fig, axes = plt.subplots(n_ax, 1, sharex=True, figsize=(9, 4.5 * n_ax))
    if n_ax == 1:
        axes = [axes]
    for ax, name in zip(axes, wanted):
        col = "va" if name == "va" else "S"
        onset_col = "t_onset_va" if name == "va" else "t_onset_S"
        status_col = "status_va" if name == "va" else "status_S"
        for row, color in items:
            _plot_b_curve(ax, row, load_series(row), col, onset_col, status_col, color, compare)
        ax.set_ylabel(r"$v_a(t)$" if col == "va" else r"$S(t)$")
        if col == "va":
            ax.set_ylim(*VA_YLIM)
        elif s_limits is not None:
            _apply_s_clip(ax, s_limits, axis="y")
        place_legend(ax, max_inside=4, fontsize=8)
    axes[-1].set_xlabel(r"Tiempo $t$")
    save(fig, stem)
    return stem


def draw_b(
    index,
    load_series,
    onset,
    *,
    series,
    fig_dir,
    compare,
    compare_dir=None,
    s_limits=None,
) -> list[Path]:
    wanted = [s.strip() for s in series.split(",")]
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    if "S" in wanted:
        s_limits = _temporal_limits(merged, load_series, s_limits)
    overlay = compare_dir or fig_dir
    stems: list[Path] = []
    if compare:
        stems.append(
            _save_b_figure(
                overlay / file_stem("f" if compare_dir else "b", "va_t" if wanted == ["va"] else "S_t"),
                wanted,
                _b_items(merged),
                load_series,
                True,
                s_limits,
            )
        )
    for model, chunk in merged.groupby("model", sort=True):
        items = _b_items(chunk)
        stems.append(
            _save_b_figure(
                fig_dir / file_stem("b", "va_t" if wanted == ["va"] else "S_t", model=model),
                wanted,
                items,
                load_series,
                compare,
                s_limits,
            )
        )
        for row, color in items:
            stems.append(
                _save_b_figure(
                    fig_dir
                    / file_stem(
                        "b",
                        "va_t" if wanted == ["va"] else "S_t",
                        model=row["model"],
                        rho=row["rho"],
                        eta=row["eta"],
                    ),
                    wanted,
                    [(row, color)],
                    load_series,
                    compare,
                    s_limits,
                )
            )
    return stems


def _plot_errorbar_curve(ax, chunk, ycol, yerr, model, rho) -> None:
    chunk = chunk.sort_values("eta")
    eta = chunk["eta"].to_numpy(dtype=float)
    y = chunk[ycol].to_numpy(dtype=float)
    err = chunk[yerr].to_numpy(dtype=float)
    # Keep NaN in y so matplotlib breaks the line. Dropping them would draw
    # η=3→4 across a point with no stationary va (the Vicsek transition).
    finite = np.isfinite(y)
    if not np.any(finite):
        return
    color = _rho_color(float(rho))
    ax.plot(
        eta,
        y,
        linestyle=_line(str(model)),
        marker=_marker(float(rho)),
        color=color,
        label=f"{_model_name(model)} | ρ={float(rho):g}",
        **_fill_kwargs(model, color),
    )
    finite_err = finite & np.isfinite(err)
    if np.any(finite_err):
        ax.errorbar(
            eta[finite_err],
            y[finite_err],
            yerr=err[finite_err],
            fmt="none",
            ecolor=color,
            capsize=4,
            elinewidth=1.2,
        )


def _draw_errorbar_frame(ax, frame, ycol, yerr) -> None:
    for (model, rho), chunk in frame.groupby(["model", "rho"], sort=True):
        _plot_errorbar_curve(ax, chunk, ycol, yerr, model, rho)


def _errorbar_xy(
    agg: pd.DataFrame,
    ycol: str,
    yerr: str,
    *,
    fig_dir,
    point: str,
    kind: str,
    ylabel,
    expected_rhos,
    compare: bool = False,
    compare_dir=None,
    ylim: tuple[float, float] | None = VA_YLIM,
    clip_s: FamilyLimits | None = None,
) -> list[Path]:
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, expected_rhos)
    kw = dict(
        figsize=(7, 4.5),
        xlabel=r"Ruido $\eta$",
        ylabel=ylabel,
        ylim=ylim,
        clip_s=clip_s,
        clip_axis="y",
    )
    overlay = compare_dir or fig_dir
    stems: list[Path] = []
    if compare:
        stems.append(
            save_curve_panel(
                overlay / file_stem("f" if compare_dir else point, kind),
                lambda ax: _draw_errorbar_frame(ax, agg, ycol, yerr),
                **kw,
            )
        )
    for model, model_chunk in agg.groupby("model", sort=True):
        stems.append(
            save_curve_panel(
                fig_dir / file_stem(point, kind, model=model),
                lambda ax, chunk=model_chunk: _draw_errorbar_frame(ax, chunk, ycol, yerr),
                **kw,
            )
        )
        for rho, rho_chunk in model_chunk.groupby("rho", sort=True):
            stems.append(
                save_curve_panel(
                    fig_dir / file_stem(point, kind, model=model, rho=rho),
                    lambda ax, chunk=rho_chunk: _draw_errorbar_frame(ax, chunk, ycol, yerr),
                    **kw,
                )
            )
    return stems


def draw_c(agg, *, fig_dir, compare=False, compare_dir=None, s_limits=None) -> list[Path]:
    if (agg.get("n_runs_va", pd.Series(dtype=float)) < 5).any():
        print("warning: (c) error bars use seed-to-seed σ; some points have n_runs_va < 5", file=sys.stderr)
    return _errorbar_xy(
        agg,
        "va_ss",
        _yerr_col(agg, "va"),
        fig_dir=fig_dir,
        point="c",
        kind="va_vs_eta",
        ylabel=r"Polarización estacionaria $\langle v_a \rangle$",
        expected_rhos=GENERAL_RHOS,
        compare=compare,
        compare_dir=compare_dir,
        ylim=VA_YLIM,
    )


def _collect_d_time_curves(merged, load_series) -> list[dict]:
    curves = []
    for (model, rho), chunk in merged.groupby(["model", "rho"], sort=True):
        etas = sorted(float(e) for e in chunk["eta"].unique())
        characteristic_eta = min(etas, key=lambda eta: abs(eta - CHARACTERISTIC_ETAS[1]))
        members = chunk.loc[np.isclose(chunk["eta"].astype(float), characteristic_eta)]
        stacked = None
        t = None
        for _, row in members.iterrows():
            data = load_series(row)
            t_run = data["t"].to_numpy()
            s = data["S"].to_numpy()
            if t is None:
                t = t_run
                stacked = s.astype(float, copy=True)
                continue
            if len(s) != len(t) or not np.array_equal(t_run, t):
                raise ValueError(f"{row['run_dir']}: S(t) series have mismatched t grids")
            stacked = stacked + s
        mean = stacked / len(members)
        usable = members.loc[members["status_S"].isin(USABLE) & members["t_onset_S"].notna()]
        t_on = float(usable["t_onset_S"].median()) if not usable.empty else None
        curves.append(
            {
                "model": str(model),
                "rho": float(rho),
                "t": t,
                "mean": mean,
                "t_on": t_on,
                "eta": characteristic_eta,
            }
        )
    return curves


def _plot_d_time_curve(ax, curve, compare) -> None:
    model = curve["model"]
    rho = curve["rho"]
    t = curve["t"]
    label = f"{_model_name(model)} | ρ={rho:g} | η={curve['eta']:g}"
    if curve["t_on"] is not None:
        label += f" | t₀={curve['t_on']:g}"
    color = _rho_color(rho)
    ax.plot(
        t,
        curve["mean"],
        linestyle=_line(model) if compare else "-",
        color=color,
        marker=_marker(rho),
        markevery=max(len(t) // 12, 1),
        alpha=0.9,
        label=label,
        **_fill_kwargs(model, color),
    )
    if curve["t_on"] is not None:
        ax.axvline(curve["t_on"], color=_rho_color(rho), linestyle="--", linewidth=1.0, alpha=0.75)


def _draw_d_time_frame(ax, curves, compare) -> None:
    for curve in curves:
        _plot_d_time_curve(ax, curve, compare)


def draw_d_time(index, load_series, onset, *, fig_dir, compare, compare_dir=None, s_limits=None) -> list[Path]:
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    present = [float(r) for r in merged["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    curves = _collect_d_time_curves(merged, load_series)
    limits = _temporal_limits(merged, load_series, s_limits)
    stems: list[Path] = []
    panel_kw = dict(
        figsize=(8, 4.5),
        xlabel=r"Tiempo $t$",
        ylabel=r"$S(t)$",
        ylim=limits.lims,
        clip_s=limits,
        clip_axis="y",
    )
    overlay = compare_dir or fig_dir

    def _panel(stem: Path, subset, use_compare: bool) -> Path:
        return save_curve_panel(
            stem,
            lambda ax, rows=subset, flag=use_compare: _draw_d_time_frame(ax, rows, flag),
            legend_kwargs={"loc": "best", "fontsize": 8, "ncols": 2 if len(subset) > 6 else 1},
            **panel_kw,
        )

    if compare:
        stems.append(_panel(overlay / file_stem("f" if compare_dir else "d", "S_t"), curves, True))
    for model in sorted({curve["model"] for curve in curves}):
        model_curves = [curve for curve in curves if curve["model"] == model]
        stems.append(_panel(fig_dir / file_stem("d", "S_t", model=model), model_curves, compare))
        for curve in model_curves:
            stems.append(
                _panel(
                    fig_dir / file_stem("d", "S_t", model=curve["model"], rho=curve["rho"]),
                    [curve],
                    compare,
                )
            )
    return stems


def draw_d_eta(agg, *, fig_dir, compare=False, compare_dir=None, s_limits=None) -> list[Path]:
    if (agg.get("n_runs_S", pd.Series(dtype=float)) < 5).any():
        print("warning: (d) error bars use seed-to-seed σ; some points have n_runs_S < 5", file=sys.stderr)
    limits = _stationary_limits(agg, s_limits)
    return _errorbar_xy(
        agg,
        "S_ss",
        _yerr_col(agg, "S"),
        fig_dir=fig_dir,
        point="d",
        kind="S_vs_eta",
        ylabel=r"Fracción estacionaria $\langle S \rangle$",
        expected_rhos=CLUSTER_RHOS,
        compare=compare,
        compare_dir=compare_dir,
        ylim=limits.lims,
        clip_s=limits,
    )


def _e_legend_handles(frame: pd.DataFrame) -> list[Line2D]:
    handles: list[Line2D] = []
    models = sorted(str(model) for model in frame["model"].unique())
    if len(models) > 1:
        for model in models:
            handles.append(
                Line2D(
                    [0],
                    [0],
                    linestyle=_line(model),
                    marker="o",
                    color="0.25",
                    label=f"Modelo: {_model_name(model)}",
                    **_fill_kwargs(model, "0.25"),
                )
            )
    for rho in sorted(float(value) for value in frame["rho"].unique()):
        color = _rho_color(rho)
        handles.append(
            Line2D(
                [0],
                [0],
                linestyle="-",
                marker=_marker(rho),
                color=color,
                label=f"Densidad ρ={rho:g}",
                markerfacecolor=color,
                markeredgecolor=color,
            )
        )
    return handles


def _add_eta_arrow(ax, x: np.ndarray, y: np.ndarray, finite: np.ndarray, color: str, model: str) -> None:
    adjacent = np.flatnonzero(finite[:-1] & finite[1:])
    if adjacent.size == 0:
        return
    distances = (x[adjacent + 1] - x[adjacent]) ** 2 + (y[adjacent + 1] - y[adjacent]) ** 2
    pair = int(adjacent[int(np.argmax(distances))])
    if distances.max() <= 0:
        return
    ax.annotate(
        "",
        xy=(x[pair + 1], y[pair + 1]),
        xytext=(x[pair], y[pair]),
        arrowprops={
            "arrowstyle": "-|>",
            "color": color,
            "linestyle": _line(model),
            "linewidth": 1.2,
            "mutation_scale": 11,
            "shrinkA": 5,
            "shrinkB": 5,
        },
        zorder=4,
    )


def _plot_e_curve(ax, chunk, model, rho) -> None:
    chunk = chunk.sort_values("eta")
    x = chunk["S_ss"].to_numpy(dtype=float)
    y = chunk["va_ss"].to_numpy(dtype=float)
    xerr = chunk[_yerr_col(chunk, "S")].to_numpy(dtype=float)
    yerr = chunk[_yerr_col(chunk, "va")].to_numpy(dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    if not np.any(finite):
        return
    color = _rho_color(float(rho))
    ax.plot(
        x,
        y,
        linestyle=_line(str(model)),
        marker=_marker(float(rho)),
        color=color,
        linewidth=1.35,
        markersize=5.5,
        zorder=3,
        **_fill_kwargs(model, color),
    )
    _add_eta_arrow(ax, x, y, finite, color, str(model))
    finite_err = finite & np.isfinite(xerr) & np.isfinite(yerr)
    if np.any(finite_err):
        ax.errorbar(
            x[finite_err],
            y[finite_err],
            xerr=xerr[finite_err],
            yerr=yerr[finite_err],
            fmt="none",
            ecolor=color,
            alpha=0.55,
            elinewidth=1.0,
            capsize=3,
            zorder=2,
        )


def _draw_e_frame(ax, frame) -> None:
    for (model, rho), chunk in frame.groupby(["model", "rho"], sort=True):
        _plot_e_curve(ax, chunk, model, rho)


def _save_e_panel(stem: Path, frame: pd.DataFrame, limits: FamilyLimits) -> Path:
    apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    _draw_e_frame(ax, frame)
    ax.set_xlabel(r"Fracción estacionaria $\langle S \rangle$")
    ax.set_ylabel(r"Polarización estacionaria $\langle v_a \rangle$")
    ax.set_xlim(*_e_xlim(limits))
    ax.set_ylim(*VA_YLIM)
    _apply_s_clip(ax, limits, axis="x")
    lo, hi = ax.get_xlim()
    span = max(hi - lo, 1.0 / limits.n_min)
    ax.set_xlim(lo, hi + max(0.08 * span, 1.0 / limits.n_min))
    handles = _e_legend_handles(frame)
    if handles:
        place_legend(ax, handles, [h.get_label() for h in handles], max_inside=8, fontsize=8)
    ax.text(
        0.02,
        0.02,
        r"Las flechas indican $\eta$ creciente",
        transform=ax.transAxes,
        fontsize=8,
        color="0.35",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 2},
    )
    save(fig, stem)
    return stem


def draw_e(agg, *, fig_dir, compare=False, compare_dir=None, s_limits=None) -> list[Path]:
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    if (agg.get("n_runs_S", pd.Series(dtype=float)) < 5).any() or (agg.get("n_runs_va", pd.Series(dtype=float)) < 5).any():
        print("warning: (e) error bars use seed-to-seed σ; some points have n_runs < 5", file=sys.stderr)
    limits = _stationary_limits(agg, s_limits)
    overlay = compare_dir or fig_dir
    stems: list[Path] = []
    if compare:
        stems.append(_save_e_panel(overlay / file_stem("f" if compare_dir else "e", "va_vs_S"), agg, limits))
    for model, model_chunk in agg.groupby("model", sort=True):
        stems.append(_save_e_panel(fig_dir / file_stem("e", "va_vs_S", model=model), model_chunk, limits))
        for rho, rho_chunk in model_chunk.groupby("rho", sort=True):
            stems.append(
                _save_e_panel(
                    fig_dir / file_stem("e", "va_vs_S", model=model, rho=rho),
                    rho_chunk,
                    _local_s_limits(rho_chunk),
                )
            )
    return stems


def _log_yerr(mean, err):
    """Barras asimetricas para eje log.

    Cuando sigma > media (distribuciones de tiempos con cola pesada) la barra
    inferior cruzaria el cero; se la trunca a una decada por debajo de la media
    (0.1*media). La superior se dibuja completa.
    """
    mean = np.asarray(mean, dtype=float)
    err = np.asarray(err, dtype=float)
    lower = np.minimum(err, 0.9 * mean)
    return np.vstack([lower, err])


def _tp1_series_label(frame: pd.DataFrame, value) -> str:
    if "serie" in frame.columns and pd.notna(value) and str(value).strip():
        return f"TP1 – {value}"
    return "TP1 – CIM"


def draw_g(
    cim_frames: list[pd.DataFrame],
    *,
    fig_dir,
    tp1: Path | None,
    tp1_n_col: str,
    tp1_t_col: str,
    labels: list[str] | None = None,
) -> list[Path]:
    apply_style()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, frame in enumerate(cim_frames):
        if labels and i < len(labels):
            label = labels[i]
        else:
            label = "TP2 – CIM" if len(cim_frames) == 1 else f"TP2 – CIM (serie {i + 1})"
        ax.errorbar(
            frame["N"],
            frame["mean_ms"],
            yerr=_log_yerr(frame["mean_ms"], frame["stdev_ns"] / 1e6) if "stdev_ns" in frame.columns else None,
            marker="o",
            color=_color(i),
            capsize=4,
            label=label,
        )
    if tp1 is not None and Path(tp1).is_file():
        extra = read_tp1_csv(Path(tp1))
        missing = [c for c in (tp1_n_col, tp1_t_col) if c not in extra.columns]
        if missing:
            raise ValueError(
                f"TP1 file {tp1} missing columns {missing}; "
                f"have {list(extra.columns)}. Pass --tp1-n-col / --tp1-t-col."
            )
        err_col = "stdev_ms" if "stdev_ms" in extra.columns else None
        groups = extra.groupby("serie", sort=False) if "serie" in extra.columns else [(None, extra)]
        for j, (serie, chunk) in enumerate(groups):
            chunk = chunk.sort_values(tp1_n_col)
            ax.errorbar(
                chunk[tp1_n_col],
                chunk[tp1_t_col],
                yerr=_log_yerr(chunk[tp1_t_col], chunk[err_col]) if err_col else None,
                linestyle="--",
                marker="s",
                color=_color(4 + j),
                capsize=4,
                label=_tp1_series_label(extra, serie),
            )
    elif tp1:
        print(f"warning: TP1 file not found ({tp1}); plotting TP2 only", file=sys.stderr)
    else:
        print("warning: no --tp1 file; plotting TP2 CIM only", file=sys.stderr)
    ax.set_xlabel(r"Cantidad de partículas $N$")
    ax.set_ylabel("Tiempo medio del CIM (ms)")
    # TP1 enunciado, punto 3: ejes en escala logaritmica cuando N o el tiempo
    # abarcan varios ordenes de magnitud (N=10..1000, t=0.01..1 ms).
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="best")
    stem = fig_dir / file_stem("g", "cim_times")
    save(fig, stem)
    return [stem]


def explore_html(agg: pd.DataFrame, path: Path) -> Path:
    ensure_dir(path.parent)
    fig = px.scatter(
        agg,
        x="eta",
        y="va_ss",
        color="model",
        symbol="rho",
        error_y=_yerr_col(agg, "va") if not agg.empty else "va_ss_std",
        hover_data=["rho", "n_runs_va", "S_ss"],
    )
    fig.write_html(path)
    return path
