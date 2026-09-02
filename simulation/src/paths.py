"""Repo-root output tree. No other module should hardcode these folders."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

KINDS = ("simulation", "figures", "animations", "explore")
POINT_FOLDERS = {
    "a": "a_animaciones",
    "b": "b_evolucion_temporal",
    "c": "c_input_vs_observable",
    "d": "d_clusters",
    "e": "e_va_vs_S",
    "f": "f_comparacion_modelos",
    "g": "g_tiempos_cim",
}


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


def expand_user_path(raw: str) -> Path:
    raw = str(raw).strip()
    if (
        sys.platform == "win32"
        and raw.startswith("/mnt/")
        and len(raw) >= 7
        and raw[5].isalpha()
        and raw[6] == "/"
    ):
        raw = f"{raw[5]}:/{raw[7:]}"
    return Path(raw).expanduser()


def resolve_scan_root(*, out: Path | None = None, batch: str | None = None, root: Path | None = None) -> Path:
    """`--out` is a path. `--batch` is a name under output/simulation, unless it is absolute."""
    base = root or repo_root()
    if out is not None:
        return Path(out)
    if not batch:
        return output_root(base)
    typed = expand_user_path(str(batch))
    if typed.is_absolute():
        return typed
    return output_root(base) / "simulation" / batch


def resolve_batch_ref(batch: str | Path, *, root: Path | None = None) -> Path:
    typed = expand_user_path(str(batch))
    if typed.is_absolute():
        return typed
    return resolve_scan_root(batch=str(batch), root=root)


def stamp(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime("%Y-%m-%d_%H%M%S")


def cache_dir(root: Path | None = None) -> Path:
    return data_dir(root) / "cache"


def data_dir(root: Path | None = None) -> Path:
    return output_root(root) / "data"


def point_dir(point: str, *, root: Path | None = None) -> Path:
    if point not in POINT_FOLDERS:
        raise ValueError(f"unknown assignment point {point!r}; expected one of {sorted(POINT_FOLDERS)}")
    return ensure_dir(output_root(root) / POINT_FOLDERS[point])


def ensure_assignment_tree(*, root: Path | None = None) -> None:
    ensure_dir(data_dir(root))
    for point in POINT_FOLDERS:
        point_dir(point, root=root)


def windows_path(path: Path) -> str | None:
    """Translate a WSL /mnt/<drive>/... path to C:\\... ; leave Windows paths as-is."""
    posix = Path(path).as_posix()
    wslpath = shutil.which("wslpath")
    if wslpath:
        completed = subprocess.run(
            [wslpath, "-w", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        mapped = completed.stdout.strip()
        if completed.returncode == 0 and mapped:
            return mapped
    if len(posix) >= 7 and posix.startswith("/mnt/") and posix[6] == "/" and posix[5].isalpha():
        return f"{posix[5].upper()}:\\{posix[7:].replace('/', '\\')}"
    if len(posix) >= 2 and posix[1] == ":":
        return str(path)
    return None


def ensure_dir(path: Path) -> Path:
    """Create a directory, including parents.

    On WSL DrvFs (/mnt/c/...) `mkdir` can raise FileExistsError while `exists()`
    is still False: a leftover NTFS/9p entry after `output/` was deleted from
    Windows. Creating the same path through cmd.exe unblocks it.
    """
    path = Path(path)
    if path.is_dir():
        return path
    if path.is_file() or path.is_symlink():
        path.unlink()
    try:
        path.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    if path.is_dir():
        return path
    if _mkdir_via_windows(path) and path.is_dir():
        return path
    raise FileExistsError(
        f"Cannot create {path}: the filesystem reports it exists but it is not "
        "a usable directory. On WSL this happens after deleting output/ from "
        "Windows. Create that folder in Explorer and retry, or run: "
        f'mkdir "{windows_path(path) or path}" from cmd.exe.'
    )


def _cmd_exe() -> str | None:
    found = shutil.which("cmd.exe")
    if found:
        return found
    bundled = Path("/mnt/c/Windows/System32/cmd.exe")
    return str(bundled) if bundled.is_file() else None


def _mkdir_via_windows(path: Path) -> bool:
    cmd = _cmd_exe()
    win = windows_path(path)
    if cmd is None or win is None:
        return False
    subprocess.run([cmd, "/c", "mkdir", win], capture_output=True, text=True, check=False)
    return path.is_dir()


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
    return ensure_dir(path)


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
