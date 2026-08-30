"""Start the Java engine. No physics."""

from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from src.paths import ensure_dir, make_batch, repo_root


class JavaProcess(Protocol):
    def run(self, argv: list[str], *, cwd: Path) -> int: ...


def _find_mvn() -> str | None:
    found = shutil.which("mvn") or shutil.which("mvn.cmd")
    if found:
        return found
    dists = Path.home() / ".m2" / "wrapper" / "dists"
    if dists.is_dir():
        matches = sorted(dists.rglob("mvn.cmd"))
        if matches:
            return str(matches[0])
    return None


@dataclass
class MavenProcess:
    mvn: str | None = None

    def run(self, argv: list[str], *, cwd: Path) -> int:
        binary = self.mvn or _find_mvn()
        if not binary:
            raise RuntimeError(
                "mvn not found on PATH; install Maven to launch the Java engine."
            )
        argv = [binary, *argv[1:]] if argv and argv[0] in {"mvn", "mvn.cmd"} else argv
        completed = subprocess.run(argv, cwd=cwd, check=False)
        return int(completed.returncode)


@dataclass
class FakeProcess:
    returncode: int = 0
    calls: list[tuple[list[str], Path]] = field(default_factory=list)

    def run(self, argv: list[str], *, cwd: Path) -> int:
        self.calls.append((list(argv), cwd))
        return self.returncode


def expand_numeric_list(raw: str) -> str:
    """Maven on Windows splits exec.args on ':'. Expand from:to:step to a comma list."""
    if ":" not in raw:
        return raw
    parts = raw.split(":")
    if len(parts) != 3:
        return raw
    start, stop, step = (float(p) for p in parts)
    if step <= 0:
        raise ValueError(f"range step must be > 0 (got {raw!r})")
    count = int(math.floor((stop - start) / step + 1e-9)) + 1
    values = []
    for i in range(count):
        value = start + i * step
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        values.append(text)
    return ",".join(values)


def _expand_cli_ranges(args: list[str]) -> list[str]:
    flags = {"--eta", "--rho", "--N"}
    out: list[str] = []
    i = 0
    while i < len(args):
        out.append(args[i])
        if args[i] in flags and i + 1 < len(args):
            out.append(expand_numeric_list(args[i + 1]))
            i += 2
            continue
        i += 1
    return out


def _join_exec_args(args: list[str]) -> str:
    parts: list[str] = []
    for arg in args:
        if any(ch.isspace() for ch in arg):
            parts.append('"' + arg.replace('"', '\\"') + '"')
        else:
            parts.append(arg)
    return " ".join(parts)


def _has_flag(args: list[str], flag: str) -> bool:
    return flag in args


def _flag_value(args: list[str], flag: str) -> str | None:
    if flag not in args:
        return None
    i = args.index(flag)
    if i + 1 >= len(args):
        raise ValueError(f"{flag} is missing a value")
    return args[i + 1]


def run_engine(
    java_args: list[str],
    *,
    out_dir: Path | None = None,
    process: JavaProcess | None = None,
    root: Path | None = None,
) -> Path:
    """Compile and run Main. A clean build avoids sharing incompatible classes across OS/JDKs."""
    repo = root or repo_root()
    args = _expand_cli_ranges(list(java_args))
    if not _has_flag(args, "--out"):
        dest = Path(out_dir) if out_dir is not None else make_batch("simulation", root=repo)
        dest = ensure_dir(dest)
        args = ["--out", str(dest.resolve()), *args]
        out_dir = dest
    else:
        out_dir = Path(_flag_value(args, "--out") or ".")

    pom = repo / "experiment" / "pom.xml"
    if not pom.is_file():
        raise FileNotFoundError(f"Missing Maven project: {pom}")

    argv = [
        "mvn",
        "-f",
        str(pom),
        "clean",
        "compile",
        "exec:java",
        f"-Dexec.args={_join_exec_args(args)}",
    ]
    runner = process or MavenProcess()
    code = runner.run(argv, cwd=repo)
    if code != 0:
        raise RuntimeError(f"Java engine exited with status {code}")
    return Path(out_dir)
