"""Argparse + questionary dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import questionary

from src.aggregate import Detector, ensemble, onset_report, warn_ranges
from src.animate import AnimateOpts, match_talk, run as animate_run
from src.io import (
    IngestResult,
    cim_label,
    default_tp1_csv,
    find_cim,
    ingest,
    iter_dynamic_frames,
    load_or_ingest,
    load_series,
    read_cim_series,
    tp1_dir,
)
from src.java import expand_numeric_list, run_engine
from src.limits import compute_s_limits
from src.paths import (
    cache_dir,
    data_dir,
    ensure_assignment_tree,
    ensure_dir,
    expand_user_path,
    make_batch,
    output_root,
    point_dir,
    repo_root,
    resolve_batch_ref,
    resolve_scan_root,
)
from src.plot import (
    FIG_CHOICES,
    default_rhos,
    draw_b,
    draw_c,
    draw_d_eta,
    draw_d_time,
    draw_e,
    draw_g,
    explore_html,
    filter_rhos,
    select_fig_b_runs,
    set_fig_formats,
)

GENERAL_RHOS = "2,4,8"
# Densidades bajas del estudio de clusters (1/(3pi), 1/(2pi), 1/pi -> N = 11, 16, 32).
# Van en su propia tanda porque con tan pocas particulas las fluctuaciones son
# enormes y necesitan mas realizaciones que las tres del enunciado.
LOW_RHOS = "0.1061,0.1592,0.3183"
PRODUCTION_ETAS = "0:6:0.5"
# rho=2,4,8: el votante a eta=0 tarda ~10^3 pasos en llegar al consenso y cerca
# de la transicion las fluctuaciones tienen tiempos de correlacion de ~10^2-10^3.
# Con N=800 son ~10 s por corrida a T=10000: la tanda completa ronda 1 h 15 min.
PRODUCTION_T = "10000"
# Con N=11..32 y v=0.03, S(t) tiene tiempos de correlacion de ~10^3 pasos: en
# T=2000 todavia parece derivar. Esas corridas son baratas (~0.3 s cada una a
# T=10000), asi que la tanda de clusters corre mucho mas larga.
LOW_T = "10000"
GENERAL_REPEATS = "5"
LOW_REPEATS = "20"
TALK_ETAS = "0.5,3.5,6"
ETA_MID = "3.5"


def _detector(ns: argparse.Namespace) -> Detector:
    return Detector(
        window=ns.window,
        atol=ns.atol,
        rtol=ns.rtol,
        t_min=ns.t_min,
        sustain=ns.sustain,
        tail_frac=getattr(ns, "tail_frac", _DEFAULT_DETECTOR.tail_frac),
        max_outside=getattr(ns, "max_outside", _DEFAULT_DETECTOR.max_outside),
    )


_DEFAULT_DETECTOR = Detector()


def _add_global(p: argparse.ArgumentParser) -> None:
    p.add_argument("--out", type=Path, default=None, help="carpeta que contiene los datos Java")
    p.add_argument(
        "--batch",
        default=None,
        help="lote existente dentro de output/simulation; permite reutilizar una simulación",
    )
    p.add_argument("--cache-dir", type=Path, default=None, help="carpeta del caché de lectura")
    p.add_argument("--fig-dir", type=Path, default=None, help="carpeta donde guardar las figuras")
    p.add_argument("--no-cache", action="store_true", help="releer los TXT aunque exista caché")
    p.add_argument(
        "--figs",
        choices=FIG_CHOICES,
        default="png",
        help="formato de las figuras estáticas (default: png)",
    )
    p.add_argument(
        "--anim",
        choices=("gif", "mp4", "both", "none"),
        default="none",
        help="formato de las animaciones del punto (a) (default: none)",
    )


def _add_steady(p: argparse.ArgumentParser) -> None:
    d = _DEFAULT_DETECTOR
    p.add_argument("--window", type=int, default=d.window, help="ancho del promedio móvil que se compara con la banda estacionaria")
    p.add_argument("--atol", type=float, default=d.atol, help="margen absoluto mínimo de la banda estacionaria")
    p.add_argument("--rtol", type=float, default=d.rtol, help="margen de la banda relativo a su ancho")
    p.add_argument("--t-min", type=int, default=d.t_min, help="primer tiempo posible del estacionario")
    p.add_argument("--sustain", type=int, default=d.sustain, help="pasos seguidos dentro de la banda para aceptar t0")
    p.add_argument("--tail-frac", type=float, default=d.tail_frac, help="fracción final de la corrida que define la banda")
    p.add_argument("--max-outside", type=float, default=d.max_outside, help="fracción máxima fuera de la banda desde t0")
    p.add_argument("--t-onset", type=int, default=None, help="forzar un mismo inicio estacionario")
    p.add_argument("--t-onset-csv", default=None, help="CSV con inicios estacionarios por corrida")


def _add_plot_filters(p: argparse.ArgumentParser) -> None:
    p.add_argument("--compare", action="store_true", help="superponer Vicsek y Votante")
    p.add_argument("--rho", default=None, help="densidades separadas por coma")
    p.add_argument("--model", default=None, help="vicsek, votante o ambos separados por coma")
    p.add_argument("--eta", default=None, help="ruidos eta separados por coma")
    p.add_argument("--runs", default=None, help="nombres de corridas separados por coma")


def _parse_floats(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def _scan_root(ns: argparse.Namespace) -> Path:
    return resolve_scan_root(out=ns.out, batch=ns.batch)


def _cache(ns: argparse.Namespace) -> Path:
    return ns.cache_dir if ns.cache_dir is not None else cache_dir()


def _print_ingest(result: IngestResult) -> None:
    for skip in result.skips:
        print(f"skip {skip.path}: {skip.reason}", file=sys.stderr)
    for msg in result.warnings:
        print(f"warning {msg}", file=sys.stderr)


def _filter_index(index, ns, *, rhos=None, runs=None):
    if index.empty:
        return index
    if ns.model:
        models = {m.strip() for m in ns.model.split(",")}
        index = index.loc[index["model"].isin(models)]
    etas = _parse_floats(getattr(ns, "eta", None))
    if etas:
        index = index.loc[index["eta"].astype(float).isin(etas)]
    if rhos:
        index = filter_rhos(index, rhos)
    if runs:
        index = index.loc[index["run_dir"].isin(set(runs))]
    return index


def _load_index(ns, *, rhos=None, runs=None):
    result = load_or_ingest(_scan_root(ns), cache=_cache(ns), no_cache=ns.no_cache)
    _print_ingest(result)
    return _filter_index(result.index, ns, rhos=rhos, runs=runs)


def prepare(ns: argparse.Namespace):
    """Ingest (or reuse a fresh cache), apply user filters, ensemble once."""
    result = load_or_ingest(_scan_root(ns), cache=_cache(ns), no_cache=ns.no_cache)
    _print_ingest(result)
    index = _filter_index(
        result.index,
        ns,
        rhos=_parse_floats(getattr(ns, "rho", None)),
        runs=_runs(ns),
    )
    onset = agg = index
    if not index.empty:
        onset, agg = _agg(ns, index)
        for line in onset_report(onset):
            print(f"warning: {line}", file=sys.stderr)
        fig_dir = getattr(ns, "fig_dir", None)
        _write_stationary_tables(onset, agg, fig_dir if fig_dir is not None else data_dir())
    return index, onset, agg


STATIONARY_COLUMNS = (
    "model", "rho", "eta", "seed", "run_dir", "T",
    "t_onset_va", "status_va", "band_lo_va", "band_hi_va",
    "t_onset_S", "status_S", "band_lo_S", "band_hi_S",
)


def _write_stationary_tables(onset, agg, dest: Path) -> None:
    """Tablas para el informe: t0 y banda por corrida, promedios por (modelo, ρ, η)."""
    dest = ensure_dir(dest)
    cols = [c for c in STATIONARY_COLUMNS if c in onset.columns]
    onset.loc[:, cols].to_csv(dest / "estacionario_por_corrida.csv", index=False)
    agg.to_csv(dest / "estacionario_promedios.csv", index=False)


def _agg(ns: argparse.Namespace, index):
    onset, agg = ensemble(
        index,
        load_series,
        _detector(ns),
        t_onset=ns.t_onset,
        t_onset_csv=ns.t_onset_csv,
    )
    return onset, agg


def _png(stem: Path) -> Path:
    return stem.parent / f"{stem.name}.png"


def _fig_dir(ns: argparse.Namespace, suffix: str) -> Path:
    if ns.fig_dir is not None:
        return ensure_dir(ns.fig_dir)
    point = {"fig-b": "b", "fig-c": "c", "fig-d": "d", "fig-e": "e", "fig-g": "g"}.get(suffix, suffix)
    if point in {"b", "c", "d", "e", "g"}:
        return point_dir(point)
    return make_batch("figures", suffix)


def _compare_dir(ns: argparse.Namespace):
    if not ns.compare:
        return None
    if ns.fig_dir is not None:
        return ensure_dir(ns.fig_dir)
    return point_dir("f")


def _resolved_anim(ns: argparse.Namespace) -> str:
    argv = [str(item) for item in getattr(ns, "_argv", [])]
    explicit = any(item == "--anim" or item.startswith("--anim=") for item in argv)
    if explicit:
        return getattr(ns, "anim", "none")
    fmt = getattr(ns, "format", None)
    if fmt:
        return fmt
    return getattr(ns, "anim", "none")


def _print_export_config(ns: argparse.Namespace) -> None:
    figs = getattr(ns, "figs", "png")
    anim = _resolved_anim(ns)
    fig_note = " (figuras salteadas)" if figs == "none" else ""
    anim_note = " (animaciones salteadas)" if anim == "none" else ""
    print(f"[config] figs={figs}{fig_note} | anim={anim}{anim_note}")


def _apply_export(ns: argparse.Namespace) -> None:
    if hasattr(ns, "figs"):
        set_fig_formats(ns.figs)
    _print_export_config(ns)
    if getattr(ns, "fig_dir", None) is None:
        ensure_assignment_tree()


def _write_s_limits(temporal, stationary) -> None:
    dest = ensure_dir(data_dir()) / "s_axis_limits.txt"
    dest.write_text(
        temporal.describe("TEMPORAL") + "\n" + stationary.describe("ESTACIONARIA") + "\n",
        encoding="utf-8",
    )
    print(temporal.describe("TEMPORAL"))
    print(stationary.describe("ESTACIONARIA"))


def _runs(ns) -> list[str] | None:
    if not getattr(ns, "runs", None):
        return None
    return [x.strip() for x in ns.runs.split(",") if x.strip()]


def _rhos_for(kind: str, ns) -> list[float] | None:
    rhos = _parse_floats(ns.rho)
    if rhos is not None:
        return rhos
    wanted = default_rhos(kind)
    return list(wanted) if wanted else None


def _slice_for_kind(kind: str, ns, index, onset, agg):
    rhos = _rhos_for(kind, ns)
    runs = _runs(ns)
    index = _filter_index(index, ns, rhos=rhos, runs=runs)
    if kind == "b" and runs is None:
        index = select_fig_b_runs(index, onset)
    if not onset.empty and "run_dir" in onset.columns:
        onset = onset.loc[onset["run_dir"].isin(index["run_dir"])]
    if not agg.empty:
        agg = filter_rhos(agg, rhos) if rhos else agg
    return index, onset, agg


def _s_limits_for(index, agg):
    if index.empty or agg.empty:
        return None, None
    temporal, stationary = compute_s_limits(index, agg, load_series)
    _write_s_limits(temporal, stationary)
    return temporal, stationary


def _render_kind(kind: str, ns, index, onset, agg, *, temporal=None, stationary=None) -> list[Path]:
    if getattr(ns, "figs", "png") == "none":
        return []
    fig_dir = _fig_dir(ns, f"fig-{kind}")
    compare = bool(ns.compare)
    compare_dir = _compare_dir(ns)
    if kind == "b":
        return draw_b(
            index,
            load_series,
            onset,
            series=getattr(ns, "series", "va"),
            fig_dir=fig_dir,
            compare=compare,
            compare_dir=compare_dir,
            s_limits=temporal,
        )
    if kind == "c":
        return draw_c(agg, fig_dir=fig_dir, compare=compare, compare_dir=compare_dir)
    if kind == "d":
        written: list[Path] = []
        panel = getattr(ns, "panel", "both")
        if panel in {"time", "both"}:
            written.extend(
                draw_d_time(
                    index,
                    load_series,
                    onset,
                    fig_dir=fig_dir,
                    compare=compare,
                    compare_dir=compare_dir,
                    s_limits=temporal,
                )
            )
        if panel in {"eta", "both"}:
            written.extend(
                draw_d_eta(
                    agg,
                    fig_dir=fig_dir,
                    compare=compare,
                    compare_dir=compare_dir,
                    s_limits=stationary,
                )
            )
        return written
    if kind == "e":
        return draw_e(
            agg,
            fig_dir=fig_dir,
            compare=compare,
            compare_dir=compare_dir,
            s_limits=stationary,
        )
    raise ValueError(f"Unknown figure kind {kind!r}")


def cmd_run(ns: argparse.Namespace) -> int:
    args = list(ns.java_args)
    if args and args[0] == "--":
        args = args[1:]
    out = run_engine(args)
    print(out)
    return 0


def cmd_ingest(ns: argparse.Namespace) -> int:
    result = ingest(_scan_root(ns), _cache(ns))
    _print_ingest(result)
    print(f"ingested {len(result.index)} runs")
    if not result.index.empty:
        for _, row in result.index.iterrows():
            series = load_series(row)
            for msg in warn_ranges(series):
                print(f"warning {row['run_dir']}: {msg}", file=sys.stderr)
    return 0


def cmd_fig(kind: str, ns: argparse.Namespace) -> int:
    _apply_export(ns)
    index, onset, agg = prepare(ns)
    if index.empty:
        raise FileNotFoundError("no runs to plot; ingest a Java output tree first")
    temporal, stationary = _s_limits_for(index, agg)
    index, onset, agg = _slice_for_kind(kind, ns, index, onset, agg)
    stems = _render_kind(kind, ns, index, onset, agg, temporal=temporal, stationary=stationary)
    for stem in stems:
        print(_png(stem))
    return 0


def cmd_fig_g(ns: argparse.Namespace) -> int:
    _apply_export(ns)
    if getattr(ns, "figs", "png") == "none":
        return 0
    cim_paths = find_cim(_scan_root(ns))
    if not cim_paths and ns.out is None:
        # El benchmark del CIM vive en su propio lote; si el lote elegido no lo
        # tiene, buscarlo en todos los lotes de output/simulation.
        cim_paths = find_cim(output_root())
        if cim_paths:
            print(f"[config] CIM: {', '.join(str(p) for p in cim_paths)}")
    if not cim_paths:
        print("warning: no hay cim_times_*.txt en ningún lote; corré `simulate -- --cim-benchmark`", file=sys.stderr)
    frames = [read_cim_series(p) for p in cim_paths]
    tp1 = getattr(ns, "tp1", None)
    if tp1 is None:
        tp1 = default_tp1_csv()
        if tp1 is not None:
            print(f"[config] TP1: {tp1}")
        else:
            print(
                f"warning: sin datos del TP1 en {tp1_dir()}; (g) muestra solo el TP2. "
                "Completá simulation/tp1/cim_times_tp1.csv (ver simulation/tp1/README.md).",
                file=sys.stderr,
            )
    stems = draw_g(
        frames,
        fig_dir=_fig_dir(ns, "fig-g"),
        labels=[cim_label(p) for p in cim_paths],
        tp1=tp1,
        tp1_n_col=getattr(ns, "tp1_n_col", "N"),
        tp1_t_col=getattr(ns, "tp1_t_col", "mean_ms"),
    )
    for stem in stems:
        print(_png(stem))
    return 0


def cmd_animate(ns: argparse.Namespace) -> int:
    _apply_export(ns)
    if _resolved_anim(ns) == "none":
        return 0
    index = _load_index(ns, rhos=_parse_floats(getattr(ns, "rho", None)), runs=_runs(ns))
    return _animate(index, ns)


def _animate(index, ns, *, talk: bool | None = None, output_format: str | None = None) -> int:
    talk = getattr(ns, "talk", False) if talk is None else talk
    rows = []
    if talk:
        rows, missing = match_talk(index, eta_mid=ns.eta_mid)
        for item in missing:
            print(f"warning: talk animation missing {item}", file=sys.stderr)
    elif getattr(ns, "run_dir", None):
        hit = index.loc[index["run_dir"] == ns.run_dir]
        if hit.empty:
            raise FileNotFoundError(ns.run_dir)
        rows = [hit.iloc[0]]
    else:
        if index.empty:
            raise FileNotFoundError("no runs with cache index")
        rows = [index.iloc[0]]
    opts = AnimateOpts(
        stride=ns.stride,
        fps=ns.fps,
        output_format=output_format or _resolved_anim(ns),
    )
    written = 0
    for row in rows:
        dyn = Path(str(row["dynamic_path"]))
        if not dyn.is_file():
            print(f"warning: no dynamic.txt for {row['run_dir']}", file=sys.stderr)
            continue
        dest_dir = point_dir("a") / str(row["run_dir"])
        ensure_dir(dest_dir)
        dest = dest_dir / "flock"
        paths = animate_run(
            iter_dynamic_frames(dyn),
            L=int(row["L"]),
            dest=dest,
            opts=opts,
        )
        for path in paths:
            print(path)
        written += 1
    if talk and written == 0:
        raise FileNotFoundError("animate --talk: no matching runs with dynamic.txt")
    return 0


def cmd_explore(ns: argparse.Namespace) -> int:
    _index, _onset, agg = prepare(ns)
    dest = make_batch("explore") / "explore.html"
    print(explore_html(agg, dest))
    return 0


def cmd_all(ns: argparse.Namespace) -> int:
    _apply_export(ns)
    index, onset, agg = prepare(ns)
    print(f"ingested {len(index)} runs")
    temporal, stationary = _s_limits_for(index, agg)
    if not index.empty:
        for kind in ("b", "c", "d", "e"):
            sliced = _slice_for_kind(kind, ns, index, onset, agg)
            for stem in _render_kind(kind, ns, *sliced, temporal=temporal, stationary=stationary):
                print(_png(stem))
    cmd_fig_g(ns)
    anim = _resolved_anim(ns)
    if anim == "none" and ns.with_animate:
        anim = "gif"
    if anim != "none":
        _animate(index, ns, talk=True, output_format=anim)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python simulation/main.py",
        description=(
            "TP2: primero genere un lote de datos de texto; después reutilice ese lote "
            "para crear figuras, animaciones o el explorador sin volver a simular."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", title="acciones")

    run_p = sub.add_parser(
        "simulate",
        aliases=["run"],
        help="generar un lote reutilizable de datos con el motor Java",
        description=(
            "Ejecuta el motor Java. Cada combinación modelo × densidad × ruido × repetición "
            "es una corrida; todas quedan juntas en un lote nuevo."
        ),
    )
    run_p.add_argument(
        "java_args",
        nargs=argparse.REMAINDER,
        help="opciones del motor después de --; use --help para abrir el asistente interactivo",
    )
    run_p.set_defaults(func=cmd_run)

    ingest_p = sub.add_parser(
        "load-data",
        aliases=["ingest"],
        help="leer o actualizar el caché de un lote ya simulado",
    )
    _add_global(ingest_p)
    ingest_p.set_defaults(func=cmd_ingest)

    figure_commands = {
        "b": (
            "time-series",
            ["fig-b"],
            "(b) graficar la evolución temporal y el inicio estacionario",
        ),
        "c": (
            "polarization-vs-noise",
            ["fig-c"],
            "(c) graficar polarización estacionaria vs. ruido con errores",
        ),
        "d": (
            "clusters",
            ["fig-d"],
            "(d) graficar S(t) y S estacionario vs. ruido",
        ),
        "e": (
            "polarization-vs-cluster",
            ["fig-e"],
            "(e) relacionar polarización y componente gigante",
        ),
    }
    for kind, (name, aliases, help_text) in figure_commands.items():
        p = sub.add_parser(name, aliases=aliases, help=help_text)
        _add_global(p)
        _add_steady(p)
        _add_plot_filters(p)
        if kind == "b":
            p.add_argument(
                "--series",
                choices=("va", "S", "va,S"),
                default="va",
                help="observable temporal a mostrar",
            )
        if kind == "d":
            p.add_argument(
                "--panel",
                choices=("time", "eta", "both"),
                default="both",
                help="evolución temporal, curva estacionaria o ambas",
            )
        p.set_defaults(func=lambda ns, k=kind: cmd_fig(k, ns))

    fig_g = sub.add_parser(
        "cim-comparison",
        aliases=["fig-g"],
        help="(g) comparar tiempos del CIM del TP2 con el TP1",
    )
    _add_global(fig_g)
    fig_g.add_argument("--tp1", type=Path, default=None, help="CSV de tiempos del TP1")
    fig_g.add_argument("--tp1-n-col", default="N", help="columna de N en el CSV del TP1")
    fig_g.add_argument("--tp1-t-col", default="mean_ms", help="columna de tiempo en el CSV del TP1")
    fig_g.set_defaults(func=cmd_fig_g)

    anim = sub.add_parser(
        "animation",
        aliases=["animate"],
        help="crear GIF/MP4 desde dynamic.txt sin volver a simular",
    )
    _add_global(anim)
    _add_steady(anim)
    _add_plot_filters(anim)
    anim.add_argument("--run-dir", default=None, help="corrida exacta dentro del lote")
    anim.add_argument("--talk", action="store_true", help="crear el catálogo de animaciones de la exposición")
    anim.add_argument("--eta-mid", type=float, default=3.5, help="ruido intermedio del catálogo")
    anim.add_argument("--stride", type=int, default=5, help="usar un frame cada N tiempos")
    anim.add_argument("--fps", type=int, default=20, help="cuadros por segundo del archivo final")
    anim.add_argument(
        "--format",
        choices=("gif", "mp4", "both"),
        default=None,
        help="alias de --anim; si ambos están, gana --anim",
    )
    anim.set_defaults(func=cmd_animate)

    exp = sub.add_parser(
        "interactive-chart",
        aliases=["explore"],
        help="crear un gráfico HTML interactivo desde un lote",
    )
    _add_global(exp)
    _add_steady(exp)
    _add_plot_filters(exp)
    exp.set_defaults(func=cmd_explore)

    all_p = sub.add_parser(
        "all-figures",
        aliases=["all"],
        help="generar todas las figuras b–g desde datos existentes",
    )
    _add_global(all_p)
    _add_steady(all_p)
    _add_plot_filters(all_p)
    all_p.add_argument(
        "--with-animate",
        action="store_true",
        help="si --anim es none, genera GIF del punto (a); preferí --anim gif|mp4|both",
    )
    all_p.add_argument("--series", default="va", help="serie para la figura b")
    all_p.add_argument("--panel", default="both", help="paneles para la figura d")
    all_p.add_argument("--tp1", type=Path, default=None, help="CSV opcional con tiempos del TP1")
    all_p.add_argument("--tp1-n-col", default="N")
    all_p.add_argument("--tp1-t-col", default="mean_ms")
    all_p.add_argument("--eta-mid", type=float, default=3.5)
    all_p.add_argument("--stride", type=int, default=5)
    all_p.add_argument("--fps", type=int, default=20)
    all_p.add_argument(
        "--format",
        choices=("gif", "mp4", "both"),
        default=None,
        help="alias de --anim",
    )
    all_p.set_defaults(func=cmd_all)

    inter = sub.add_parser("interactive", help="abrir el asistente guiado")
    inter.set_defaults(func=lambda ns: interactive())
    return parser


def _batch_dirs() -> list[Path]:
    root = output_root(repo_root()) / "simulation"
    if not root.is_dir():
        return []
    return sorted((path for path in root.iterdir() if path.is_dir()), reverse=True)


def _batch_cli_args(batch: str | Path) -> list[str]:
    path = expand_user_path(str(batch)) if not isinstance(batch, Path) else batch
    if path.is_absolute():
        return ["--out", str(path.resolve())]
    return ["--batch", str(batch)]


def _expand_user_path(raw: str) -> Path:
    return expand_user_path(raw)


def _ask_typed_batch_path() -> Path | None:
    while True:
        raw = questionary.text(
            "Pegá la ruta completa del lote (Windows C:\\... o WSL /mnt/c/...):",
        ).ask()
        if raw is None:
            return None
        if not str(raw).strip():
            print("error: el path no puede estar vacío", file=sys.stderr)
            continue
        path = _expand_user_path(raw)
        resolved = path.resolve()
        if resolved.is_dir():
            return resolved
        print(f"error: no existe el directorio {path}", file=sys.stderr)


def _choose_batch(
    prompt: str = "Elegí el lote de datos que querés reutilizar:",
    *,
    need_runs: bool = False,
    need_dynamic: bool = False,
    need_cim: bool = False,
) -> str | Path | None:
    write_path = object()
    choices = []
    for batch in _batch_dirs():
        runs = [path for path in batch.iterdir() if path.is_dir() and (path / "observables.txt").is_file()]
        dynamic = sum((path / "dynamic.txt").is_file() for path in runs)
        cim = len(find_cim(batch))
        if need_runs and not runs:
            continue
        if need_dynamic and dynamic == 0:
            continue
        if need_cim and cim == 0:
            continue
        title = f"{batch.name} — {len(runs)} corridas, {dynamic} animables, {cim} series CIM"
        choices.append(questionary.Choice(title=title, value=batch))
    choices.append(questionary.Choice(title="Escribir un path...", value=write_path))
    selected = questionary.select(prompt, choices=choices).ask()
    if selected is None:
        return None
    if selected is write_path:
        return _ask_typed_batch_path()
    return selected


def _interactive_custom_simulate() -> int:
    model = questionary.select(
        "Modelo (cada opción genera corridas independientes):",
        choices=[
            questionary.Choice("Ambos — Vicsek y Votante para poder compararlos", value="both"),
            questionary.Choice("Vicsek — promedia las direcciones vecinas", value="vicsek"),
            questionary.Choice("Votante — copia la dirección de un vecino", value="votante"),
        ],
    ).ask()
    if model is None:
        return 1
    rho = questionary.text(
        "Densidades rho separadas por coma (N=rho*L^2):",
        default="2,4,8",
    ).ask()
    eta = questionary.text(
        "Ruidos eta; lista 0,0.5,1 o rango desde:hasta:paso:",
        default="0:6:0.5",
    ).ask()
    steps = questionary.text(
        "Pasos T por corrida (500 en el perfil productivo actual):",
        default="500",
    ).ask()
    repeats = questionary.text(
        "Repeticiones por combinación (semillas distintas; necesarias para barras de error):",
        default="1",
    ).ask()
    seed = questionary.text("Semilla base reproducible:", default="1").ask()
    dynamic = questionary.confirm(
        "¿Guardar posiciones y velocidades (dynamic.txt) para poder animar? Ocupa mucho más espacio.",
        default=False,
    ).ask()
    answers = (rho, eta, steps, repeats, seed, dynamic)
    if any(answer is None for answer in answers):
        return 1
    args = [
        "--model",
        model,
        "--rho",
        rho,
        "--eta",
        eta,
        "--T",
        steps,
        "--repeats",
        repeats,
        "--seed",
        seed,
    ]
    if dynamic:
        args.append("--dynamic")
    summary = (
        f"modelo={model}, rho={rho}, eta={eta}, T={steps}, repeticiones={repeats}, "
        f"dynamic.txt={'sí' if dynamic else 'no'}"
    )
    if not questionary.confirm(f"¿Generar este lote? {summary}", default=True).ask():
        return 1
    out = run_engine(args)
    print(f"Datos guardados en: {out}")
    print("Podés reutilizar este lote todas las veces que quieras sin volver a simular.")
    if questionary.confirm(
        "¿Querés elegir ahora qué figuras o animaciones generar con estos datos?",
        default=True,
    ).ask():
        return _interactive_outputs(out)
    return 0


def _n_values(raw: str) -> int:
    """Cuantos valores genera una lista o un rango `desde:hasta:paso` de Java."""
    return len(expand_numeric_list(raw).split(","))


def _n_runs(rhos: str, etas: str, repeats: str, *, models: int = 2) -> int:
    return models * _n_values(rhos) * _n_values(etas) * int(repeats)


def _sweep_args(rhos: str, repeats: str, steps: str = PRODUCTION_T) -> list[str]:
    return [
        "--model",
        "both",
        "--rho",
        rhos,
        "--eta",
        PRODUCTION_ETAS,
        "--T",
        steps,
        "--repeats",
        repeats,
        "--seed",
        "1",
    ]


def _production_args() -> list[tuple[str, list[str]]]:
    """Las dos tandas del barrido, etiquetadas.

    Van separadas porque `--repeats` es global en Java y las densidades bajas
    (N entre 11 y 32) necesitan mas realizaciones para que las barras de error de
    (d) y (e) sirvan. Comparten lote de salida, asi que el ingest las ve juntas.
    """
    return [
        (f"densidades del enunciado rho={{{GENERAL_RHOS}}}", _sweep_args(GENERAL_RHOS, GENERAL_REPEATS)),
        (f"densidades de clusters rho={{{LOW_RHOS}}}", _sweep_args(LOW_RHOS, LOW_REPEATS, LOW_T)),
    ]


def _production_run_counts() -> tuple[int, int]:
    return (
        _n_runs(GENERAL_RHOS, PRODUCTION_ETAS, GENERAL_REPEATS),
        _n_runs(LOW_RHOS, PRODUCTION_ETAS, LOW_REPEATS),
    )


def _production_summary() -> str:
    general, low = _production_run_counts()
    return (
        f"{general + low} corridas "
        f"({general} en rho={{{GENERAL_RHOS}}} x{GENERAL_REPEATS} con T={PRODUCTION_T}, "
        f"{low} en rho={{{LOW_RHOS}}} x{LOW_REPEATS} con T={LOW_T})"
    )


def _talk_args() -> list[list[str]]:
    """Catalogo de animaciones: las tres densidades del enunciado con ruido
    bajo/medio/alto, mas las de clusters a ruido medio (cada estudio necesita su
    propia animacion caracteristica)."""
    base = ["--model", "both", "--T", "2000", "--seed", "1", "--dynamic"]
    return [
        ["--rho", GENERAL_RHOS, "--eta", TALK_ETAS, *base],
        ["--rho", LOW_RHOS, "--eta", ETA_MID, *base],
    ]


def _talk_run_count() -> int:
    return _n_runs(GENERAL_RHOS, TALK_ETAS, "1") + _n_runs(LOW_RHOS, ETA_MID, "1")


def _confirm_production() -> bool:
    return bool(
        questionary.confirm(
            f"El barrido completo ejecuta {_production_summary()}. "
            "¿La máquina está lista para continuar?",
            default=False,
        ).ask()
    )


def _generate_production_data(*, confirm: bool = True) -> Path | None:
    if confirm and not _confirm_production():
        return None
    out = make_batch("simulation")
    for label, args in _production_args():
        print(f"Generando barrido productivo — {label}...")
        run_engine(args, out_dir=out)
    print(f"Barrido guardado en: {out}")
    return out


def _generate_talk_data() -> Path:
    out = make_batch("simulation", "animaciones")
    print(f"Generando {_talk_run_count()} corridas animables: ambos modelos, "
          f"rho={{{GENERAL_RHOS}}} con ruido bajo/medio/alto y rho={{{LOW_RHOS}}} a ruido medio...")
    for args in _talk_args():
        run_engine(args, out_dir=out)
    print(f"Datos animables guardados en: {out}")
    return out


def _generate_cim_data() -> Path:
    print("Ejecutando benchmark del Cell Index Method...")
    out = run_engine(["--cim-benchmark"])
    print(f"Benchmark guardado en: {out}")
    return out


def _interactive_generate_data() -> int:
    profile = questionary.select(
        "¿Qué datos querés generar?",
        choices=[
            questionary.Choice(
                f"Barrido completo del TP — {_production_summary()}, sin dynamic.txt",
                value="production",
            ),
            questionary.Choice(
                f"Corridas para animaciones — {_talk_run_count()} corridas con dynamic.txt",
                value="talk",
            ),
            questionary.Choice(
                "Benchmark del CIM — tiempos necesarios para el punto (g)",
                value="cim",
            ),
            questionary.Choice(
                "Configuración personalizada — elegir modelo, densidad, ruido y T",
                value="custom",
            ),
        ],
    ).ask()
    if profile is None:
        return 1
    if profile == "production":
        return 0 if _generate_production_data() is not None else 1
    if profile == "talk":
        _generate_talk_data()
        return 0
    if profile == "cim":
        _generate_cim_data()
        return 0
    return _interactive_custom_simulate()


def _interactive_animations(batch: str | Path) -> int:
    batch_path = resolve_batch_ref(batch)
    result = load_or_ingest(batch_path, cache=cache_dir())
    _print_ingest(result)
    if result.index.empty or "dynamic_path" not in result.index.columns:
        print(f"error: el lote {batch} no contiene corridas válidas", file=sys.stderr)
        return 1
    rows = result.index.loc[result.index["dynamic_path"].map(lambda path: Path(str(path)).is_file())]
    if rows.empty:
        print(
            "error: ninguna corrida de este lote tiene dynamic.txt; generá los datos con --dynamic",
            file=sys.stderr,
        )
        return 1
    choices = [
        questionary.Choice(
            title=(
                f"{row['run_dir']} — {_model_name_for_cli(row['model'])}, "
                f"rho={row['rho']:g}, eta={row['eta']:g}, semilla={row['seed']}"
            ),
            value=str(row["run_dir"]),
        )
        for _, row in rows.iterrows()
    ]
    selected = questionary.checkbox(
        "Elegí una o más corridas a animar (se reutiliza su dynamic.txt):",
        choices=choices,
    ).ask()
    if not selected:
        return 1
    output_format = questionary.select(
        "Formato de animación:",
        choices=[
            questionary.Choice("GIF y MP4", value="both"),
            questionary.Choice("Solo MP4", value="mp4"),
            questionary.Choice("Solo GIF", value="gif"),
        ],
    ).ask()
    if output_format is None:
        return 1
    code = 0
    for run_dir in selected:
        argv = ["animation", *_batch_cli_args(batch_path), "--run-dir", run_dir, "--format", output_format]
        print("python simulation/main.py " + " ".join(argv))
        code = max(code, main(argv))
    return code


def _model_name_for_cli(model: str) -> str:
    return "Vicsek" if str(model) == "vicsek" else "Votante"


def _interactive_outputs(batch: str | Path | None = None) -> int:
    products = questionary.checkbox(
        "¿Qué resultados querés generar desde datos existentes?",
        choices=[
            questionary.Choice("(b) Evolución temporal de va(t) y comienzo estacionario", value="time-series"),
            questionary.Choice("(c) Polarización estacionaria vs. ruido eta", value="polarization-vs-noise"),
            questionary.Choice("(d) Evolución y valor estacionario del cluster gigante S", value="clusters"),
            questionary.Choice("(e) Polarización va vs. componente gigante S", value="polarization-vs-cluster"),
            questionary.Choice("Animaciones GIF/MP4 de corridas con dynamic.txt", value="animation"),
            questionary.Choice("Gráfico HTML interactivo para explorar resultados", value="interactive-chart"),
            questionary.Choice("(g) Comparación de tiempos del CIM", value="cim-comparison"),
        ],
    ).ask()
    if not products:
        return 1
    figure_products = {
        "time-series",
        "polarization-vs-noise",
        "clusters",
        "polarization-vs-cluster",
    }
    analysis_products = {*figure_products, "interactive-chart"}
    analysis_batch = batch
    if analysis_products.intersection(products) and analysis_batch is None:
        analysis_batch = _choose_batch(
            "Elegí el lote con observables para los gráficos:",
            need_runs=True,
        )
        if analysis_batch is None:
            return 1
    animation_batch = batch
    if "animation" in products and animation_batch is None:
        animation_batch = _choose_batch(
            "Elegí el lote que contiene dynamic.txt:",
            need_dynamic=True,
        )
        if animation_batch is None:
            return 1
    cim_batch = None
    if "cim-comparison" in products:
        cim_batch = _choose_batch(
            "Elegí el lote que contiene los tiempos del CIM:",
            need_cim=True,
        )
        if cim_batch is None:
            return 1
    compare = False
    if figure_products.intersection(products):
        compare = bool(
            questionary.confirm(
                "¿Superponer Vicsek y Votante cuando ambos estén en el lote?",
                default=True,
            ).ask()
        )
    code = 0
    for product in products:
        if product == "animation":
            code = max(code, _interactive_animations(animation_batch))
            continue
        selected_batch = cim_batch if product == "cim-comparison" else analysis_batch
        argv = [product, *_batch_cli_args(selected_batch)]
        if compare and product in figure_products:
            argv.append("--compare")
        if product == "cim-comparison":
            tp1 = _ask_tp1_csv()
            if tp1 is not None:
                argv.extend(["--tp1", str(tp1)])
        print("python simulation/main.py " + " ".join(argv))
        code = max(code, main(argv))
    return code


def _ask_tp1_csv() -> Path | None:
    bundled = default_tp1_csv()
    if bundled is not None:
        print(f"Tiempos del TP1: {bundled}")
        return bundled
    has_tp1 = questionary.confirm(
        f"No hay tiempos del TP1 en {tp1_dir()}. ¿Tenés otro CSV con los tiempos medidos en el TP1?",
        default=False,
    ).ask()
    if not has_tp1:
        return None
    raw = questionary.text(
        "Pegá la ruta completa del CSV del TP1:",
    ).ask()
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_file():
        print(f"warning: no existe {path}; se graficará solamente TP2", file=sys.stderr)
        return None
    return path


def _generate_assignment_outputs(
    analysis_batch: str | Path,
    animation_batch: str | Path,
    cim_batch: str | Path,
    *,
    tp1: Path | None,
) -> int:
    code = 0
    for product in (
        "time-series",
        "polarization-vs-noise",
        "clusters",
        "polarization-vs-cluster",
    ):
        argv = [product, *_batch_cli_args(analysis_batch), "--compare"]
        print("python simulation/main.py " + " ".join(argv))
        code = max(code, main(argv))

    animation_argv = ["animation", *_batch_cli_args(animation_batch), "--talk", "--anim", "both"]
    print("python simulation/main.py " + " ".join(animation_argv))
    code = max(code, main(animation_argv))

    cim_argv = ["cim-comparison", *_batch_cli_args(cim_batch)]
    if tp1 is not None:
        cim_argv.extend(["--tp1", str(tp1)])
    print("python simulation/main.py " + " ".join(cim_argv))
    code = max(code, main(cim_argv))
    print(f"Figuras del TP guardadas en: {output_root() / 'c_input_vs_observable'} y carpetas hermanas")
    return code


def _existing_assignment_batches() -> tuple[str | Path, str | Path, str | Path] | None:
    analysis = _choose_batch(
        "Lote del barrido completo (observables para b–f):",
        need_runs=True,
    )
    if analysis is None:
        return None
    animations = _choose_batch(
        "Lote de las 18 corridas animables (dynamic.txt):",
        need_dynamic=True,
    )
    if animations is None:
        return None
    cim = _choose_batch(
        "Lote del benchmark del CIM:",
        need_cim=True,
    )
    if cim is None:
        return None
    return analysis, animations, cim


def _interactive_all() -> int:
    source = questionary.select(
        "¿Cómo querés hacer todos los puntos del enunciado?",
        choices=[
            questionary.Choice(
                "Reutilizar datos existentes — no vuelve a simular",
                value="existing",
            ),
            questionary.Choice(
                "Ejecutar todo desde cero — barrido, animaciones y benchmark",
                value="scratch",
            ),
        ],
    ).ask()
    if source is None:
        return 1

    if source == "existing":
        batches = _existing_assignment_batches()
        if batches is None:
            return 1
        analysis, animations, cim = batches
    else:
        if not _confirm_production():
            return 1
        print("Etapa 1/3: barrido productivo.")
        analysis_path = _generate_production_data(confirm=False)
        if analysis_path is None:
            return 1
        print("Etapa 2/3: corridas para animaciones.")
        animations_path = _generate_talk_data()
        print("Etapa 3/3: benchmark del CIM.")
        cim_path = _generate_cim_data()
        analysis, animations, cim = analysis_path, animations_path, cim_path

    tp1 = _ask_tp1_csv()
    if tp1 is None:
        print(
            "warning: sin datos del TP1, el punto (g) mostrará los tiempos del TP2 pero no la comparación completa",
            file=sys.stderr,
        )
    return _generate_assignment_outputs(analysis, animations, cim, tp1=tp1)


def interactive() -> int:
    action = questionary.select(
        "Flujo del TP2 — ¿qué querés hacer?",
        choices=[
            questionary.Choice(
                "1. Generar datos — barrido, animaciones, CIM o corrida personalizada",
                value="data",
            ),
            questionary.Choice(
                "2. Generar resultados — elegir gráficos/animaciones desde datos existentes",
                value="results",
            ),
            questionary.Choice(
                "3. Hacer todo el TP — puntos (a) a (g)",
                value="all",
            ),
        ],
    ).ask()
    if action is None:
        return 1
    if action == "data":
        return _interactive_generate_data()
    if action == "results":
        return _interactive_outputs()
    return _interactive_all()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    parser = _build_parser()
    try:
        if not argv:
            return interactive()
        ns = parser.parse_args(argv)
        ns._argv = argv
        if not getattr(ns, "cmd", None):
            return interactive()
        return int(ns.func(ns))
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
