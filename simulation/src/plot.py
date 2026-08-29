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

from src.aggregate import USABLE
from src.io import rho_close

GENERAL_RHOS = (2.0, 4.0, 8.0)
CLUSTER_RHOS = GENERAL_RHOS
CHARACTERISTIC_ETAS = (0.5, 3.5, 6.0)

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


def apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 200,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.axisbelow": True,
            "legend.frameon": True,
            "lines.linewidth": 1.5,
            "lines.markersize": 5,
        }
    )


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.parent / f"{stem.name}.png", bbox_inches="tight")
    fig.savefig(stem.parent / f"{stem.name}.pdf", bbox_inches="tight")
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
    ax.legend(**(legend_kwargs or {"loc": "best"}))
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


def _model_name(model: str) -> str:
    return "Vicsek" if str(model) == "vicsek" else "Votante"


def _curve_tag(model, rho=None, eta=None) -> str:
    parts = [str(model)]
    if rho is not None:
        parts.append(f"rho{float(rho):g}")
    if eta is not None:
        parts.append(f"eta{float(eta):g}")
    return "-".join(parts)


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


def select_fig_b_runs(index: pd.DataFrame) -> pd.DataFrame:
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
    sort_cols = [column for column in ("model", "eta", "seed", "run_dir") if column in chosen.columns]
    chosen = chosen.sort_values(sort_cols)
    return chosen.drop_duplicates(subset=["model", "eta"], keep="first")


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


def _save_b_figure(stem: Path, wanted: list[str], items, load_series, compare) -> Path:
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
        ax.set_ylim(0, 1.02)
        ax.legend(loc="best", fontsize=8, ncols=2 if len(items) > 6 else 1)
    axes[-1].set_xlabel(r"Tiempo $t$")
    save(fig, stem)
    return stem


def draw_b(index, load_series, onset, *, series, fig_dir, compare) -> list[Path]:
    wanted = [s.strip() for s in series.split(",")]
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    stems: list[Path] = []
    if compare:
        items = _b_items(merged)
        stems.append(_save_b_figure(fig_dir / "fig-b", wanted, items, load_series, True))
        for row, color in items:
            stem = fig_dir / f"fig-b-{_curve_tag(row['model'], row['rho'], row['eta'])}"
            stems.append(_save_b_figure(stem, wanted, [(row, color)], load_series, True))
        return stems
    for model, chunk in merged.groupby("model", sort=True):
        items = _b_items(chunk)
        stems.append(_save_b_figure(fig_dir / f"fig-b-{model}", wanted, items, load_series, False))
        for row, color in items:
            stem = fig_dir / f"fig-b-{_curve_tag(row['model'], row['rho'], row['eta'])}"
            stems.append(_save_b_figure(stem, wanted, [(row, color)], load_series, False))
    return stems


def _plot_errorbar_curve(ax, chunk, ycol, yerr, model, rho) -> None:
    chunk = chunk.sort_values("eta")
    y = chunk[ycol].to_numpy()
    err = chunk[yerr].to_numpy()
    finite_err = np.isfinite(err)
    ax.plot(
        chunk["eta"],
        y,
        linestyle=_line(str(model)),
        marker=_marker(float(rho)),
        color=_rho_color(float(rho)),
        label=f"{_model_name(model)} | ρ={float(rho):g}",
    )
    if np.any(finite_err):
        ax.errorbar(
            chunk["eta"].to_numpy()[finite_err],
            y[finite_err],
            yerr=err[finite_err],
            fmt="none",
            ecolor=_rho_color(float(rho)),
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
    stem_prefix,
    ylabel,
    expected_rhos,
) -> list[Path]:
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, expected_rhos)
    kw = dict(
        figsize=(7, 4.5),
        xlabel=r"Ruido $\eta$",
        ylabel=ylabel,
        ylim=(0, 1.02),
    )
    stems: list[Path] = []
    for model, model_chunk in agg.groupby("model", sort=True):
        stems.append(
            save_curve_panel(
                fig_dir / f"{stem_prefix}-{_curve_tag(model)}",
                lambda ax, chunk=model_chunk: _draw_errorbar_frame(ax, chunk, ycol, yerr),
                **kw,
            )
        )
        for rho, rho_chunk in model_chunk.groupby("rho", sort=True):
            stems.append(
                save_curve_panel(
                    fig_dir / f"{stem_prefix}-{_curve_tag(model, rho)}",
                    lambda ax, chunk=rho_chunk: _draw_errorbar_frame(ax, chunk, ycol, yerr),
                    **kw,
                )
            )
    return stems


def draw_c(agg, *, fig_dir, compare=False) -> list[Path]:
    return _errorbar_xy(
        agg,
        "va_ss",
        "va_ss_err",
        fig_dir=fig_dir,
        stem_prefix="fig-c",
        ylabel=r"Polarización estacionaria $\langle v_a \rangle$",
        expected_rhos=GENERAL_RHOS,
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
    ax.plot(
        t,
        curve["mean"],
        linestyle=_line(model) if compare else "-",
        color=_rho_color(rho),
        marker=_marker(rho),
        markevery=max(len(t) // 12, 1),
        alpha=0.9,
        label=label,
    )
    if curve["t_on"] is not None:
        ax.axvline(curve["t_on"], color=_rho_color(rho), linestyle="--", linewidth=1.0, alpha=0.75)


def _draw_d_time_frame(ax, curves, compare) -> None:
    for curve in curves:
        _plot_d_time_curve(ax, curve, compare)


def draw_d_time(index, load_series, onset, *, fig_dir, compare) -> list[Path]:
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    present = [float(r) for r in merged["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    curves = _collect_d_time_curves(merged, load_series)
    stems: list[Path] = []
    panel_kw = dict(
        figsize=(8, 4.5),
        xlabel=r"Tiempo $t$",
        ylabel=r"$S(t)$",
        ylim=(0, 1.02),
    )

    def _panel(stem: Path, subset, use_compare: bool) -> Path:
        return save_curve_panel(
            stem,
            lambda ax, rows=subset, flag=use_compare: _draw_d_time_frame(ax, rows, flag),
            legend_kwargs={"loc": "best", "fontsize": 8, "ncols": 2 if len(subset) > 6 else 1},
            **panel_kw,
        )

    if compare:
        stems.append(_panel(fig_dir / "fig-d-S-t", curves, True))
        for curve in curves:
            stem = fig_dir / f"fig-d-S-t-{_curve_tag(curve['model'], curve['rho'])}"
            stems.append(_panel(stem, [curve], True))
        return stems
    for model in sorted({curve["model"] for curve in curves}):
        model_curves = [curve for curve in curves if curve["model"] == model]
        stems.append(_panel(fig_dir / f"fig-d-S-t-{_curve_tag(model)}", model_curves, False))
        for curve in model_curves:
            stem = fig_dir / f"fig-d-S-t-{_curve_tag(curve['model'], curve['rho'])}"
            stems.append(_panel(stem, [curve], False))
    return stems


def draw_d_eta(agg, *, fig_dir, compare=False) -> list[Path]:
    return _errorbar_xy(
        agg,
        "S_ss",
        "S_ss_err",
        fig_dir=fig_dir,
        stem_prefix="fig-d-S-eta",
        ylabel=r"Fracción estacionaria $\langle S \rangle$",
        expected_rhos=CLUSTER_RHOS,
    )


def _plot_e_curve(ax, chunk, model, rho) -> None:
    chunk = chunk.sort_values("eta")
    ax.plot(
        chunk["S_ss"],
        chunk["va_ss"],
        linestyle=_line(str(model)),
        marker=_marker(float(rho)),
        color=_rho_color(float(rho)),
        label=f"{_model_name(model)} | ρ={float(rho):g}",
    )


def _draw_e_frame(ax, frame) -> None:
    for (model, rho), chunk in frame.groupby(["model", "rho"], sort=True):
        _plot_e_curve(ax, chunk, model, rho)


def draw_e(agg, *, fig_dir, compare=False) -> list[Path]:
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    kw = dict(
        figsize=(6.5, 6),
        xlabel=r"Fracción estacionaria $\langle S \rangle$",
        ylabel=r"Polarización estacionaria $\langle v_a \rangle$",
        xlim=(0, 1.02),
        ylim=(0, 1.02),
        legend_kwargs={"loc": "best", "fontsize": 8},
    )
    stems: list[Path] = []
    if compare:
        stems.append(save_curve_panel(fig_dir / "fig-e", lambda ax: _draw_e_frame(ax, agg), **kw))
    for model, model_chunk in agg.groupby("model", sort=True):
        stems.append(
            save_curve_panel(
                fig_dir / f"fig-e-{_curve_tag(model)}",
                lambda ax, chunk=model_chunk: _draw_e_frame(ax, chunk),
                **kw,
            )
        )
        for rho, rho_chunk in model_chunk.groupby("rho", sort=True):
            stems.append(
                save_curve_panel(
                    fig_dir / f"fig-e-{_curve_tag(model, rho)}",
                    lambda ax, chunk=rho_chunk: _draw_e_frame(ax, chunk),
                    **kw,
                )
            )
    return stems


def draw_g(cim_frames: list[pd.DataFrame], *, fig_dir, tp1: Path | None, tp1_n_col: str, tp1_t_col: str) -> list[Path]:
    apply_style()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, frame in enumerate(cim_frames):
        ax.errorbar(
            frame["N"],
            frame["mean_ms"],
            yerr=frame["stdev_ns"] / 1e6 if "stdev_ns" in frame.columns else None,
            marker="o",
            color=_color(i),
            capsize=4,
            label="TP2 – CIM" if len(cim_frames) == 1 else f"TP2 – CIM (serie {i + 1})",
        )
    if tp1 is not None and Path(tp1).is_file():
        extra = pd.read_csv(tp1)
        missing = [c for c in (tp1_n_col, tp1_t_col) if c not in extra.columns]
        if missing:
            raise ValueError(
                f"TP1 file {tp1} missing columns {missing}; "
                f"have {list(extra.columns)}. Pass --tp1-n-col / --tp1-t-col."
            )
        ax.plot(extra[tp1_n_col], extra[tp1_t_col], linestyle="--", marker="s", color=_color(4), label="TP1")
    elif tp1:
        print(f"warning: TP1 file not found ({tp1}); plotting TP2 only", file=sys.stderr)
    else:
        print("warning: no --tp1 file; plotting TP2 CIM only", file=sys.stderr)
    ax.set_xlabel(r"Cantidad de partículas $N$")
    ax.set_ylabel("Tiempo medio del CIM (ms)")
    ax.legend(loc="best")
    stem = fig_dir / "fig-g"
    save(fig, stem)
    return [stem]


def explore_html(agg: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = px.scatter(
        agg,
        x="eta",
        y="va_ss",
        color="model",
        symbol="rho",
        error_y="va_ss_err",
        hover_data=["rho", "n_runs_va", "S_ss"],
    )
    fig.write_html(path)
    return path
