"""Argparse + questionary dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import questionary

from src.aggregate import Detector, ensemble, warn_ranges
from src.animate import AnimateOpts, match_talk, run as animate_run
from src.io import (
    IngestResult,
    find_cim,
    ingest,
    iter_dynamic_frames,
    load_or_ingest,
    load_series,
    read_cim_series,
)
from src.java import run_engine
from src.paths import cache_dir, make_batch, output_root, repo_root
from src.plot import (
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
)


def _detector(ns: argparse.Namespace) -> Detector:
    return Detector(
        window=ns.window,
        atol=ns.atol,
        rtol=ns.rtol,
        t_min=ns.t_min,
        sustain=ns.sustain,
    )


def _add_global(p: argparse.ArgumentParser) -> None:
    p.add_argument("--out", type=Path, default=None, help="Java output tree (default: <repo>/output)")
    p.add_argument("--batch", default=None, help="restrict to output/simulation/<batch>")
    p.add_argument("--cache-dir", type=Path, default=None)
    p.add_argument("--fig-dir", type=Path, default=None)
    p.add_argument("--no-cache", action="store_true")


def _add_steady(p: argparse.ArgumentParser) -> None:
    p.add_argument("--window", type=int, default=200)
    p.add_argument("--atol", type=float, default=0.02)
    p.add_argument("--rtol", type=float, default=0.05)
    p.add_argument("--t-min", type=int, default=200)
    p.add_argument("--sustain", type=int, default=3)
    p.add_argument("--t-onset", type=int, default=None)
    p.add_argument("--t-onset-csv", default=None)


def _add_plot_filters(p: argparse.ArgumentParser) -> None:
    p.add_argument("--compare", action="store_true")
    p.add_argument("--rho", default=None, help="comma-separated densities")
    p.add_argument("--model", default=None)
    p.add_argument("--eta", default=None)
    p.add_argument("--runs", default=None, help="comma-separated run directory names")


def _parse_floats(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def _scan_root(ns: argparse.Namespace) -> Path:
    root = repo_root()
    if ns.out is not None:
        return ns.out
    if ns.batch:
        return output_root(root) / "simulation" / ns.batch
    return output_root(root)


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


def _agg(ns: argparse.Namespace, index):
    onset, agg = ensemble(
        index,
        load_series,
        _detector(ns),
        t_onset=ns.t_onset,
        t_onset_csv=ns.t_onset_csv,
    )
    return onset, agg


def _fig_dir(ns: argparse.Namespace, suffix: str) -> Path:
    if ns.fig_dir is not None:
        ns.fig_dir.mkdir(parents=True, exist_ok=True)
        return ns.fig_dir
    return make_batch("figures", suffix)


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
        index = select_fig_b_runs(index)
    if not onset.empty and "run_dir" in onset.columns:
        onset = onset.loc[onset["run_dir"].isin(index["run_dir"])]
    if not agg.empty:
        agg = filter_rhos(agg, rhos) if rhos else agg
    return index, onset, agg


def _render_kind(kind: str, ns, index, onset, agg) -> list[Path]:
    fig_dir = _fig_dir(ns, f"fig-{kind}")
    compare = bool(ns.compare)
    if kind == "b":
        return draw_b(
            index,
            load_series,
            onset,
            series=getattr(ns, "series", "va"),
            fig_dir=fig_dir,
            compare=compare,
        )
    if kind == "c":
        return draw_c(agg, fig_dir=fig_dir)
    if kind == "d":
        written: list[Path] = []
        panel = getattr(ns, "panel", "both")
        if panel in {"time", "both"}:
            written.append(draw_d_time(index, load_series, fig_dir=fig_dir, compare=compare))
        if panel in {"eta", "both"}:
            written.append(draw_d_eta(agg, fig_dir=fig_dir))
        return written
    if kind == "e":
        return draw_e(agg, fig_dir=fig_dir)
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
    if kind == "g":
        return cmd_fig_g(ns)
    index = _load_index(ns, rhos=_rhos_for(kind, ns), runs=_runs(ns))
    if kind == "b" and _runs(ns) is None:
        index = select_fig_b_runs(index)
    if index.empty:
        raise FileNotFoundError("no runs to plot; ingest a Java output tree first")
    onset, agg = _agg(ns, index)
    stems = _render_kind(kind, ns, index, onset, agg)
    for stem in stems:
        print(stem.with_suffix(".png"))
    return 0


def cmd_fig_g(ns: argparse.Namespace) -> int:
    frames = [read_cim_series(p) for p in find_cim(_scan_root(ns))]
    stems = draw_g(
        frames,
        fig_dir=_fig_dir(ns, "fig-g"),
        tp1=getattr(ns, "tp1", None),
        tp1_n_col=getattr(ns, "tp1_n_col", "N"),
        tp1_t_col=getattr(ns, "tp1_t_col", "mean_ms"),
    )
    for stem in stems:
        print(stem.with_suffix(".png"))
    return 0


def cmd_animate(ns: argparse.Namespace) -> int:
    index = _load_index(ns)
    return _animate(index, ns)


def _animate(index, ns, *, talk: bool | None = None) -> int:
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
    opts = AnimateOpts(stride=ns.stride, fps=ns.fps, gif=ns.gif)
    written = 0
    for row in rows:
        dyn = Path(str(row["dynamic_path"]))
        if not dyn.is_file():
            print(f"warning: no dynamic.txt for {row['run_dir']}", file=sys.stderr)
            continue
        dest_dir = make_batch("animations", str(row["run_dir"]))
        dest = dest_dir / "flock.mp4"
        path = animate_run(
            iter_dynamic_frames(dyn),
            L=int(row["L"]),
            dest=dest,
            opts=opts,
        )
        print(path)
        written += 1
    if talk and written == 0:
        raise FileNotFoundError("animate --talk: no matching runs with dynamic.txt")
    return 0


def cmd_explore(ns: argparse.Namespace) -> int:
    index = _load_index(ns)
    _onset, agg = _agg(ns, index)
    dest = make_batch("explore") / "explore.html"
    print(explore_html(agg, dest))
    return 0


def cmd_all(ns: argparse.Namespace) -> int:
    result = ingest(_scan_root(ns), _cache(ns))
    _print_ingest(result)
    print(f"ingested {len(result.index)} runs")
    index = _filter_index(result.index, ns)
    onset = agg = index
    if not index.empty:
        onset, agg = _agg(ns, index)
        for kind in ("b", "c", "d", "e"):
            sliced = _slice_for_kind(kind, ns, index, onset, agg)
            for stem in _render_kind(kind, ns, *sliced):
                print(stem.with_suffix(".png"))
    cmd_fig_g(ns)
    if ns.with_animate:
        _animate(index, ns, talk=True)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python simulation/main.py")
    sub = parser.add_subparsers(dest="cmd")

    run_p = sub.add_parser("run", help="start the Java engine")
    run_p.add_argument("java_args", nargs=argparse.REMAINDER)
    run_p.set_defaults(func=cmd_run)

    ingest_p = sub.add_parser("ingest")
    _add_global(ingest_p)
    ingest_p.set_defaults(func=cmd_ingest)

    for kind in ("b", "c", "d", "e", "g"):
        p = sub.add_parser(f"fig-{kind}")
        _add_global(p)
        _add_steady(p)
        _add_plot_filters(p)
        if kind == "b":
            p.add_argument("--series", default="va")
        if kind == "d":
            p.add_argument("--panel", choices=("time", "eta", "both"), default="both")
        if kind == "g":
            p.add_argument("--tp1", type=Path, default=None)
            p.add_argument("--tp1-n-col", default="N")
            p.add_argument("--tp1-t-col", default="mean_ms")
        p.set_defaults(func=lambda ns, k=kind: cmd_fig(k, ns))

    anim = sub.add_parser("animate")
    _add_global(anim)
    _add_steady(anim)
    _add_plot_filters(anim)
    anim.add_argument("--run-dir", default=None)
    anim.add_argument("--talk", action="store_true")
    anim.add_argument("--eta-mid", type=float, default=3.5)
    anim.add_argument("--stride", type=int, default=5)
    anim.add_argument("--fps", type=int, default=20)
    anim.add_argument("--gif", action="store_true")
    anim.set_defaults(func=cmd_animate)

    exp = sub.add_parser("explore")
    _add_global(exp)
    _add_steady(exp)
    _add_plot_filters(exp)
    exp.set_defaults(func=cmd_explore)

    all_p = sub.add_parser("all")
    _add_global(all_p)
    _add_steady(all_p)
    _add_plot_filters(all_p)
    all_p.add_argument("--with-animate", action="store_true")
    all_p.add_argument("--series", default="va")
    all_p.add_argument("--panel", default="both")
    all_p.add_argument("--tp1", type=Path, default=None)
    all_p.add_argument("--tp1-n-col", default="N")
    all_p.add_argument("--tp1-t-col", default="mean_ms")
    all_p.add_argument("--eta-mid", type=float, default=3.5)
    all_p.add_argument("--stride", type=int, default=5)
    all_p.add_argument("--fps", type=int, default=20)
    all_p.add_argument("--gif", action="store_true")
    all_p.set_defaults(func=cmd_all)

    inter = sub.add_parser("interactive")
    inter.set_defaults(func=lambda ns: interactive())
    return parser


def interactive() -> int:
    action = questionary.select(
        "What do you want to do?",
        choices=["run Java", "ingest", "fig-b", "fig-c", "fig-d", "fig-e", "fig-g", "animate --talk"],
    ).ask()
    if action is None:
        return 1
    if action == "run Java":
        extra = questionary.text("Java args (after --)").ask() or ""
        argv = ["run", "--", *extra.split()]
    elif action == "ingest":
        argv = ["ingest"]
    elif action == "animate --talk":
        argv = ["animate", "--talk"]
    else:
        compare = questionary.confirm("Overlay both models (--compare)?", default=True).ask()
        argv = [action]
        if compare:
            argv.append("--compare")
    print("python simulation/main.py " + " ".join(argv))
    return main(argv)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    parser = _build_parser()
    if not argv:
        return interactive()
    ns = parser.parse_args(argv)
    if not getattr(ns, "cmd", None):
        return interactive()
    try:
        return int(ns.func(ns))
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
