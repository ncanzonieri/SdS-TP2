"""Particle animations from dynamic.txt, exported as GIF and/or MP4."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None

from src.io import rho_close

TALK_MODELS = ("vicsek", "votante")
TALK_RHOS = (2.0, 4.0, 8.0)
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


# Display-only: Java v is typically 0.03 in a box of L=10, so quiver in data
# units (scale_units="xy", scale=1) draws invisible arrows. Keep direction;
# do not change the Java speed.
DISPLAY_ARROW_FRAC = 0.04


def display_uv(vx, vy, L: float) -> tuple[np.ndarray, np.ndarray]:
    """Quiver U,V for display. Direction only; length is L * DISPLAY_ARROW_FRAC."""
    vx = np.asarray(vx, dtype=float)
    vy = np.asarray(vy, dtype=float)
    speed = np.hypot(vx, vy)
    length = float(L) * DISPLAY_ARROW_FRAC
    ux = np.zeros_like(vx)
    uy = np.zeros_like(vy)
    ok = speed > 0
    ux[ok] = vx[ok] / speed[ok] * length
    uy[ok] = vy[ok] / speed[ok] * length
    return ux, uy


@dataclass
class AnimateOpts:
    stride: int = 5
    fps: int = 20
    output_format: str = "both"


def run(
    frames,
    *,
    L: int,
    dest: Path,
    opts: AnimateOpts | None = None,
) -> tuple[Path, ...]:
    opts = opts or AnimateOpts()
    if opts.output_format not in {"gif", "mp4", "both"}:
        raise ValueError(f"unknown animation format: {opts.output_format}")
    if opts.output_format in {"mp4", "both"} and imageio_ffmpeg is None:
        raise RuntimeError(
            "MP4 export requires imageio-ffmpeg; install simulation/requirements.txt "
            "or use --format gif"
        )
    sampled = list(frames)
    if opts.stride > 1:
        sampled = sampled[:: opts.stride]
    if not sampled:
        raise ValueError("no frames to animate")

    dest.parent.mkdir(parents=True, exist_ok=True)
    t0, xy0 = sampled[0]
    x, y, vx, vy = xy0[:, 0], xy0[:, 1], xy0[:, 2], xy0[:, 3]
    c = theta(vx, vy)
    ux, uy = display_uv(vx, vy, L)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    q = ax.quiver(
        x,
        y,
        ux,
        uy,
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
        du, dv = display_uv(xy[:, 2], xy[:, 3], L)
        q.set_offsets(xy[:, :2])
        q.set_UVC(du, dv, theta(xy[:, 2], xy[:, 3]))
        title.set_text(f"t = {t}")
        return q, title

    anim = FuncAnimation(fig, update, frames=sampled, blit=False, interval=1000 / opts.fps)
    written: list[Path] = []
    if opts.output_format in {"gif", "both"}:
        gif = dest.with_suffix(".gif")
        anim.save(gif, writer=PillowWriter(fps=opts.fps))
        written.append(gif)
    if opts.output_format in {"mp4", "both"}:
        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        mp4 = dest.with_suffix(".mp4")
        anim.save(mp4, writer=FFMpegWriter(fps=opts.fps))
        written.append(mp4)
    plt.close(fig)
    return tuple(written)


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
