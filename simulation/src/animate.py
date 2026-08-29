"""Particle animations from dynamic.txt. ffmpeg is a system binary."""

from __future__ import annotations

import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.io import rho_close

TALK_MODELS = ("vicsek", "votante")
TALK_RHOS = (2.0, 8.0)
ETA_MID = 3.5


def talk_catalog(eta_mid: float = ETA_MID) -> tuple[tuple[str, float, float], ...]:
    return tuple(
        (model, rho, eta)
        for model in TALK_MODELS
        for eta in (0.5, eta_mid, 6.0)
        for rho in TALK_RHOS
    )


TALK_ANIMATIONS = talk_catalog()


def theta(vx, vy) -> np.ndarray:
    ang = np.arctan2(np.asarray(vy, dtype=float), np.asarray(vx, dtype=float))
    return np.mod(ang, 2.0 * math.pi)


@dataclass
class AnimateOpts:
    stride: int = 5
    fps: int = 20
    gif: bool = False


def run(
    frames,
    *,
    L: int,
    dest: Path,
    opts: AnimateOpts | None = None,
) -> Path:
    opts = opts or AnimateOpts()
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found on PATH; install ffmpeg (system package, not pip) to export MP4"
        )
    # Agg must be selected before pyplot; importing this module must not change the process backend.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

    sampled = list(frames)
    if opts.stride > 1:
        sampled = sampled[:: opts.stride]
    if not sampled:
        raise ValueError("no frames to animate")

    dest.parent.mkdir(parents=True, exist_ok=True)
    t0, xy0 = sampled[0]
    x, y, vx, vy = xy0[:, 0], xy0[:, 1], xy0[:, 2], xy0[:, 3]
    c = theta(vx, vy)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    q = ax.quiver(
        x,
        y,
        vx,
        vy,
        c,
        cmap="hsv",
        clim=(0.0, 2.0 * math.pi),
        scale_units="xy",
        scale=1,
        width=0.004,
    )
    title = ax.set_title(f"t = {t0}")

    def update(item):
        t, xy = item
        q.set_offsets(xy[:, :2])
        q.set_UVC(xy[:, 2], xy[:, 3], theta(xy[:, 2], xy[:, 3]))
        title.set_text(f"t = {t}")
        return q, title

    anim = FuncAnimation(fig, update, frames=sampled, blit=False, interval=1000 / opts.fps)
    mp4 = dest.with_suffix(".mp4") if dest.suffix != ".mp4" else dest
    writer = FFMpegWriter(fps=opts.fps)
    anim.save(mp4, writer=writer)
    if opts.gif:
        anim.save(mp4.with_suffix(".gif"), writer=PillowWriter(fps=opts.fps))
    plt.close(fig)
    return mp4


def match_talk(index, *, eta_mid: float = ETA_MID):
    wanted = talk_catalog(eta_mid)
    rows = []
    missing = []
    for model, rho, eta in wanted:
        hit = index.loc[
            (index["model"] == model)
            & np.isclose(index["eta"].astype(float), eta)
            & index["rho"].map(lambda r, target=rho: rho_close(float(r), target))
        ]
        if hit.empty:
            missing.append((model, rho, eta))
        else:
            rows.append(hit.iloc[0])
    return rows, missing
