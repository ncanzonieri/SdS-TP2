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
# Java writes rho = N/L^2 (L=10 → 0.32, 0.16, 0.11) for the cluster densities
# 1/π, 1/(2π), 1/(3π). Defaults match those folder names; rho_close aliases
# both styles (including fixture rho0.3183).
CLUSTER_RHOS = (0.32, 0.16, 0.11, 2.0, 4.0, 8.0)

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
    fig.savefig(stem.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


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
    pick = {etas[0], etas[-1]}
    chosen = at_rho.loc[at_rho["eta"].map(lambda e: float(e) in pick)]
    if len(chosen) > 12:
        print("warning: fig-b overlay has more than 12 series", file=sys.stderr)
    return chosen


def draw_b(index, load_series, onset, *, series, fig_dir, compare) -> list[Path]:
    apply_style()
    wanted = [s.strip() for s in series.split(",")]
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    n_ax = len(wanted)
    fig, axes = plt.subplots(n_ax, 1, sharex=True, figsize=(9, 4.5 * n_ax))
    if n_ax == 1:
        axes = [axes]
    for ax, name in zip(axes, wanted):
        col = "va" if name == "va" else "S"
        onset_col = "t_onset_va" if name == "va" else "t_onset_S"
        status_col = "status_va" if name == "va" else "status_S"
        for i, (_, row) in enumerate(merged.iterrows()):
            data = load_series(row)
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
                color=_color(i),
                alpha=0.9,
                label=label,
            )
            if status in USABLE and pd.notna(t_on):
                ax.axvline(float(t_on), color=_color(i), linestyle="--", linewidth=1.0, alpha=0.75)
        ax.set_ylabel(r"$v_a(t)$" if col == "va" else r"$S(t)$")
        ax.set_ylim(0, 1.02)
        ax.set_title(
            "Evolución temporal de la polarización"
            if col == "va"
            else "Evolución temporal de la componente gigante"
        )
        ax.legend(loc="best", fontsize=8, ncols=2 if len(merged) > 6 else 1)
    axes[-1].set_xlabel(r"Tiempo $t$")
    stem = fig_dir / "fig-b"
    save(fig, stem)
    return [stem]


def _errorbar_xy(
    agg: pd.DataFrame,
    ycol: str,
    yerr: str,
    n_runs_col: str,
    *,
    fig_dir,
    stem_name,
    ylabel,
    title,
    expected_rhos,
):
    apply_style()
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, expected_rhos)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    warned_single = False
    for model_rho, chunk in agg.groupby(["model", "rho"], sort=True):
        model, rho = model_rho
        chunk = chunk.sort_values("eta")
        y = chunk[ycol].to_numpy()
        err = chunk[yerr].to_numpy()
        n_runs = chunk[n_runs_col].to_numpy()
        finite_err = (n_runs > 1) & np.isfinite(err)
        if np.any(n_runs <= 1):
            warned_single = True
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
    if warned_single:
        print("warning: n_runs=1; drawing the point with no error bar", file=sys.stderr)
    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1.02)
    ax.set_title(title)
    ax.legend(loc="best")
    stem = fig_dir / stem_name
    save(fig, stem)
    return stem


def draw_c(agg, *, fig_dir) -> list[Path]:
    stem = _errorbar_xy(
        agg,
        "va_ss",
        "va_ss_std",
        "n_runs_va",
        fig_dir=fig_dir,
        stem_name="fig-c",
        ylabel=r"Polarización estacionaria $\langle v_a \rangle$",
        title="Polarización estacionaria en función del ruido",
        expected_rhos=GENERAL_RHOS,
    )
    return [stem]


def draw_d_time(index, load_series, onset, *, fig_dir, compare) -> Path:
    apply_style()
    merged = index.merge(_onset_cols(onset), on="run_dir", how="left")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    present = [float(r) for r in merged["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    for (model, rho), chunk in merged.groupby(["model", "rho"], sort=True):
        etas = sorted(float(e) for e in chunk["eta"].unique())
        eta0 = etas[0]
        members = chunk.loc[np.isclose(chunk["eta"].astype(float), eta0)]
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
        label = f"{_model_name(model)} | ρ={float(rho):g} | η={eta0:g}"
        if t_on is not None:
            label += f" | t₀={t_on:g}"
        ax.plot(
            t,
            mean,
            linestyle=_line(str(model)) if compare else "-",
            color=_rho_color(float(rho)),
            marker=_marker(float(rho)),
            markevery=max(len(t) // 12, 1),
            alpha=0.9,
            label=label,
        )
        if t_on is not None:
            ax.axvline(t_on, color=_rho_color(float(rho)), linestyle="--", linewidth=1.0, alpha=0.75)
    ax.set_xlabel(r"Tiempo $t$")
    ax.set_ylabel(r"$S(t)$")
    ax.set_ylim(0, 1.02)
    ax.set_title("Evolución temporal de la componente gigante")
    ax.legend(loc="best", fontsize=8, ncols=2 if len(merged) > 6 else 1)
    stem = fig_dir / "fig-d-S-t"
    save(fig, stem)
    return stem


def draw_d_eta(agg, *, fig_dir) -> Path:
    return _errorbar_xy(
        agg,
        "S_ss",
        "S_ss_std",
        "n_runs_S",
        fig_dir=fig_dir,
        stem_name="fig-d-S-eta",
        ylabel=r"Fracción estacionaria $\langle S \rangle$",
        title="Componente gigante estacionaria en función del ruido",
        expected_rhos=CLUSTER_RHOS,
    )


def draw_e(agg, *, fig_dir) -> list[Path]:
    apply_style()
    present = [float(r) for r in agg["rho"].unique()]
    warn_missing_rhos(present, CLUSTER_RHOS)
    fig, ax = plt.subplots(figsize=(6.5, 6))
    for (model, rho), chunk in agg.groupby(["model", "rho"], sort=True):
        chunk = chunk.sort_values("eta")
        ax.plot(
            chunk["S_ss"],
            chunk["va_ss"],
            linestyle=_line(str(model)),
            marker=_marker(float(rho)),
            color=_rho_color(float(rho)),
            label=f"{_model_name(model)} | ρ={float(rho):g}",
        )
    ax.set_xlabel(r"Fracción estacionaria $\langle S \rangle$")
    ax.set_ylabel(r"Polarización estacionaria $\langle v_a \rangle$")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_title("Polarización y componente gigante")
    ax.legend(loc="best", fontsize=8)
    stem = fig_dir / "fig-e"
    save(fig, stem)
    return [stem]


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
    ax.set_title("Comparación de tiempos de ejecución del CIM")
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
        error_y="va_ss_std",
        hover_data=["rho", "n_runs_va", "S_ss"],
    )
    fig.write_html(path)
    return path
