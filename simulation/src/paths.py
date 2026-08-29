"""Repo-root output tree. No other module should hardcode these folders."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

KINDS = ("simulation", "figures", "animations", "explore")


def repo_root(start: Path | None = None) -> Path:
    here = start.resolve() if start is not None else Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "experiment").is_dir() and (candidate / "simulation").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not find the repo root (expected sibling folders experiment/ and simulation/)."
    )


def output_root(root: Path | None = None) -> Path:
    return (root or repo_root()) / "output"


def stamp(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")


def cache_dir(root: Path | None = None) -> Path:
    return output_root(root) / "cache"


def make_batch(
    kind: str,
    suffix: str | None = None,
    *,
    root: Path | None = None,
    when: datetime | None = None,
) -> Path:
    if kind not in KINDS:
        raise ValueError(f"Unknown batch kind {kind!r}; expected one of {KINDS}")
    name = stamp(when)
    if suffix:
        name = f"{name}_{suffix}"
    path = output_root(root) / kind / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def iter_batch_dirs(scan_root: Path) -> list[Path]:
    """Timestamped Java batches under output/simulation, or the path itself."""
    if not scan_root.exists():
        return []
    if scan_root.name == "output":
        sim = scan_root / "simulation"
        if not sim.is_dir():
            return []
        return sorted(p for p in sim.iterdir() if p.is_dir())
    if scan_root.name == "simulation" and scan_root.parent.name == "output":
        return sorted(p for p in scan_root.iterdir() if p.is_dir())
    return [scan_root]
