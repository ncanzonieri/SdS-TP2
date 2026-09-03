"""Java text loaders, run-dir names, and the raw-series cache."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

from src.paths import cache_dir, ensure_dir, iter_batch_dirs

RUN_DIR_RE = re.compile(
    r"^(?P<model>vicsek|votante)"
    r"_rho(?P<rho>[0-9.]+)"
    r"_eta(?P<eta>[0-9.]+)"
    r"_T(?P<T>\d+)"
    r"_seed(?P<seed>-?\d+)"
    r"(?:_r(?P<repeat>\d+))?$"
)

INDEX_COLUMNS = (
    "model",
    "rho",
    "eta",
    "T",
    "seed",
    "repeat",
    "N",
    "L",
    "run_dir",
    "batch",
    "series_path",
    "dynamic_path",
)


@dataclass(frozen=True)
class RunMeta:
    model: str
    rho: float
    eta: float
    T: int
    seed: int
    repeat: int | None = None


@dataclass(frozen=True)
class Run:
    path: Path
    meta: RunMeta
    batch: str
    N: int
    L: int


@dataclass(frozen=True)
class Skip:
    path: Path
    reason: str


def fmt(value: float) -> str:
    text = f"{value:.4f}".rstrip("0")
    return text[:-1] if text.endswith(".") else text


def parse_run_dirname(name: str) -> RunMeta | None:
    match = RUN_DIR_RE.fullmatch(name)
    if match is None:
        return None
    repeat_raw = match.group("repeat")
    return RunMeta(
        model=match.group("model"),
        rho=float(match.group("rho")),
        eta=float(match.group("eta")),
        T=int(match.group("T")),
        seed=int(match.group("seed")),
        repeat=None if repeat_raw is None else int(repeat_raw),
    )


def format_run_dirname(meta: RunMeta) -> str:
    name = (
        f"{meta.model}_rho{fmt(meta.rho)}_eta{fmt(meta.eta)}"
        f"_T{meta.T}_seed{meta.seed}"
    )
    if meta.repeat is not None:
        name = f"{name}_r{meta.repeat}"
    return name


def read_static(path: Path) -> tuple[int, int]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < 2:
        raise ValueError(f"{path}: static.txt needs two lines (N, L)")
    return int(lines[0]), int(lines[1])


def read_observables(path: Path) -> pd.DataFrame:
    try:
        frame = pd.read_csv(
            path,
            sep=r"\s+",
            comment="#",
            names=["t", "va", "S"],
            header=None,
            dtype={"t": int, "va": float, "S": float},
            engine="python",
        )
    except (ValueError, pd.errors.ParserError) as exc:
        raise ValueError(f"{path}: could not parse observables.txt") from exc
    if frame.empty:
        raise ValueError(f"{path}: observables.txt has no data rows")
    if frame[["t", "va", "S"]].isna().any().any():
        raise ValueError(f"{path}: truncated or corrupt observables.txt")
    return frame.reset_index(drop=True)


def iter_dynamic_frames(path: Path) -> Iterator[tuple[int, np.ndarray]]:
    with path.open(encoding="utf-8") as handle:
        while True:
            header = handle.readline()
            if not header:
                return
            header = header.strip()
            if not header:
                continue
            t = int(header)
            rows: list[list[float]] = []
            peek_pos = handle.tell()
            line = handle.readline()
            while line:
                parts = line.split()
                if len(parts) == 1:
                    handle.seek(peek_pos)
                    break
                if len(parts) != 4:
                    raise ValueError(f"{path}: bad dynamic row at t={t}: {line!r}")
                rows.append([float(x) for x in parts])
                peek_pos = handle.tell()
                line = handle.readline()
            if not rows:
                raise ValueError(f"{path}: empty frame at t={t}")
            yield t, np.asarray(rows, dtype=float)


def read_cim_series(path: Path) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 4:
                raise ValueError(f"{path}: expected N L mean_ns stdev_ns [mean_ms], got {stripped!r}")
            rec = {
                "N": int(parts[0]),
                "L": int(parts[1]),
                "mean_ns": float(parts[2]),
                "stdev_ns": float(parts[3]),
            }
            rec["mean_ms"] = float(parts[4]) if len(parts) >= 5 else rec["mean_ns"] / 1e6
            rows.append(rec)
    if not rows:
        raise ValueError(f"{path}: no CIM data rows")
    return pd.DataFrame(rows)


def cim_label(path: Path) -> str:
    """Leyenda de una serie del benchmark a partir del nombre de archivo."""
    name = Path(path).stem
    if name.startswith("cim_times_L"):
        return f"TP2 – CIM (L={name[len('cim_times_L'):]} fijo)"
    if name == "cim_times_rho_fixed":
        return "TP2 – CIM (ρ fija, L crece con N)"
    return f"TP2 – CIM ({name})"


def tp1_dir() -> Path:
    """Carpeta dentro de `simulation/` con los tiempos medidos en el TP1."""
    return Path(__file__).resolve().parents[1] / "tp1"


TP1_CSV_NAME = "cim_times_tp1.csv"


def read_tp1_csv(path: Path) -> pd.DataFrame:
    """CSV del TP1: lineas `#` son comentarios; tiene que traer N y un tiempo."""
    frame = pd.read_csv(path, comment="#", skip_blank_lines=True)
    frame.columns = [str(c).strip() for c in frame.columns]
    return frame.dropna(how="all")


def default_tp1_csv() -> Path | None:
    """El CSV del TP1 si existe y ya tiene datos (no solo el encabezado)."""
    path = tp1_dir() / TP1_CSV_NAME
    if not path.is_file():
        return None
    try:
        frame = read_tp1_csv(path)
    except (ValueError, pd.errors.ParserError):
        return None
    return path if not frame.empty else None


def find_cim(out_dir: Path) -> list[Path]:
    files: list[Path] = []
    for batch in iter_batch_dirs(out_dir):
        files.extend(sorted(batch.glob("cim_times_*.txt")))
    files.extend(sorted(out_dir.glob("cim_times_*.txt")))
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def scan_runs(out_dir: Path) -> tuple[list[Run], list[Skip]]:
    if out_dir.is_dir() and (out_dir / "static.txt").is_file():
        meta = parse_run_dirname(out_dir.name)
        if meta is None:
            return [], [Skip(out_dir, "name does not match Java run-dir pattern")]
        n, L = read_static(out_dir / "static.txt")
        return [Run(out_dir, meta, out_dir.parent.name, n, L)], []

    batches = iter_batch_dirs(out_dir)
    runs: list[Run] = []
    skips: list[Skip] = []
    for batch in batches:
        if not batch.is_dir():
            continue
        for child in sorted(batch.iterdir()):
            if not child.is_dir():
                continue
            meta = parse_run_dirname(child.name)
            if meta is None:
                skips.append(Skip(child, "name does not match Java run-dir pattern"))
                continue
            static = child / "static.txt"
            obs = child / "observables.txt"
            if not static.is_file():
                skips.append(Skip(child, "missing static.txt"))
                continue
            if not obs.is_file():
                skips.append(Skip(child, "missing observables.txt"))
                continue
            try:
                n, L = read_static(static)
            except (ValueError, OSError) as exc:
                skips.append(Skip(child, str(exc)))
                continue
            runs.append(Run(child, meta, batch.name, n, L))
    return runs, skips


def _series_path(cache: Path, batch: str, run_dir: str) -> Path:
    return cache / "series" / batch / f"{run_dir}.csv.gz"


@dataclass
class IngestResult:
    index: pd.DataFrame
    skips: list[Skip]
    warnings: list[str]


def ingest(out_dir: Path, dest: Path | None = None) -> IngestResult:
    cache = dest or cache_dir()
    cache = ensure_dir(cache)
    runs, skips = scan_runs(out_dir)
    warnings: list[str] = []
    records: list[dict] = []
    for run in runs:
        try:
            obs = read_observables(run.path / "observables.txt")
        except (ValueError, OSError) as exc:
            skips.append(Skip(run.path, str(exc)))
            continue
        series = _series_path(cache, run.batch, run.path.name)
        ensure_dir(series.parent)
        obs.to_csv(series, index=False, compression="gzip")
        dynamic = run.path / "dynamic.txt"
        expected_n = int(round(run.meta.rho * run.L * run.L))
        if run.N != expected_n:
            warnings.append(f"{run.path}: N={run.N} vs round(rho*L^2)={expected_n} (loaded anyway)")
        records.append(
            {
                "model": run.meta.model,
                "rho": run.meta.rho,
                "eta": run.meta.eta,
                "T": run.meta.T,
                "seed": run.meta.seed,
                "repeat": 0 if run.meta.repeat is None else run.meta.repeat,
                "N": run.N,
                "L": run.L,
                "run_dir": run.path.name,
                "batch": run.batch,
                "series_path": str(series),
                "dynamic_path": str(dynamic) if dynamic.is_file() else "",
            }
        )
    index = pd.DataFrame(records, columns=list(INDEX_COLUMNS))
    index.to_csv(cache / "index.csv.gz", index=False, compression="gzip")
    return IngestResult(index, skips, warnings)


def load_index(dest: Path | None = None) -> pd.DataFrame:
    path = (dest or cache_dir()) / "index.csv.gz"
    if not path.is_file():
        raise FileNotFoundError(f"No cache index at {path}; run ingest first or pass --no-cache")
    return pd.read_csv(path, compression="gzip")


def load_series(row: pd.Series) -> pd.DataFrame:
    path = Path(str(row["series_path"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path, compression="gzip")


def _path_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def java_tree_mtime(out_dir: Path) -> float:
    """Newest mtime of batch dirs and run files. Used to invalidate a stale cache."""
    if not out_dir.exists():
        return 0.0
    latest = _path_mtime(out_dir)
    batches = iter_batch_dirs(out_dir)
    if not batches and out_dir.is_dir():
        batches = [out_dir]
    for batch in batches:
        latest = max(latest, _path_mtime(batch))
        if not batch.is_dir():
            continue
        for child in batch.iterdir():
            latest = max(latest, _path_mtime(child))
            if child.is_dir():
                for name in ("static.txt", "observables.txt", "dynamic.txt"):
                    target = child / name
                    if target.is_file():
                        latest = max(latest, _path_mtime(target))
        for cim in batch.glob("cim_times_*.txt"):
            latest = max(latest, _path_mtime(cim))
    if out_dir.is_dir():
        for cim in out_dir.glob("cim_times_*.txt"):
            latest = max(latest, _path_mtime(cim))
    return latest


def _listed_run_names(out_dir: Path) -> set[str]:
    names: set[str] = set()
    if (out_dir / "static.txt").is_file():
        if parse_run_dirname(out_dir.name) is not None:
            names.add(out_dir.name)
        return names
    for batch in iter_batch_dirs(out_dir):
        if not batch.is_dir():
            continue
        for child in batch.iterdir():
            if child.is_dir() and parse_run_dirname(child.name) is not None:
                names.add(child.name)
    return names


def load_or_ingest(
    out_dir: Path,
    *,
    cache: Path | None = None,
    no_cache: bool = False,
) -> IngestResult:
    dest = cache or cache_dir()
    index_path = dest / "index.csv.gz"
    if no_cache or not index_path.is_file():
        return ingest(out_dir, dest)
    if java_tree_mtime(out_dir) > index_path.stat().st_mtime:
        return ingest(out_dir, dest)
    index = load_index(dest)
    known = set(index["run_dir"].astype(str)) if not index.empty and "run_dir" in index.columns else set()
    if not _listed_run_names(out_dir).issubset(known):
        return ingest(out_dir, dest)
    batches = {p.name for p in iter_batch_dirs(out_dir)}
    if (out_dir / "static.txt").is_file():
        index = index.loc[index["run_dir"] == out_dir.name].copy()
    elif batches and "batch" in index.columns:
        index = index.loc[index["batch"].isin(batches)].copy()
    return IngestResult(index, [], [])


# Java folder names use rho = N/L^2 (L=10 → 0.32, 0.16, 0.11) even when the
# requested density was 1/π, 1/(2π), 1/(3π). Fixture dirs keep rho0.3183.
# abs_tol must cover |0.11 - 1/(3π)| ≈ 3.9e-3 without merging 0.16 vs 0.11.
RHO_ABS_TOL = 5.5e-3


def rho_close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0, abs_tol=RHO_ABS_TOL)
