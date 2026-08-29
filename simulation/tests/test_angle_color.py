import math

import numpy as np
import pandas as pd

from src.animate import (
    DISPLAY_ARROW_FRAC,
    TALK_ANIMATIONS,
    TALK_CLUSTER_RHOS,
    TALK_RHOS,
    display_uv,
    match_talk,
    theta,
)


def test_display_uv_keeps_direction_scales_length():
    L = 10.0
    ux, uy = display_uv([0.03], [0.0], L)
    assert abs(ux[0] - L * DISPLAY_ARROW_FRAC) < 1e-12
    assert abs(uy[0]) < 1e-12
    ux, uy = display_uv([0.0], [-0.03], L)
    assert abs(ux[0]) < 1e-12
    assert abs(uy[0] + L * DISPLAY_ARROW_FRAC) < 1e-12


def test_quadrants_and_wrap():
    ang = theta(np.array([1.0, 0.0, -1.0, 0.0]), np.array([0.0, 1.0, 0.0, -1.0]))
    assert abs(ang[0] - 0.0) < 1e-9
    assert abs(ang[1] - math.pi / 2) < 1e-9
    assert abs(ang[2] - math.pi) < 1e-9
    assert abs(ang[3] - (3 * math.pi / 2)) < 1e-9
    wrapped = theta(np.array([1.0]), np.array([-1e-15]))
    assert 0.0 <= wrapped[0] < 2 * math.pi


def test_near_cut_close_in_hue():
    a = theta(np.array([1.0]), np.array([0.01]))[0]
    b = theta(np.array([1.0]), np.array([-0.01]))[0]
    # hsv is cyclic; the angular difference wrapping 0 should be small
    delta = min(abs(a - b), 2 * math.pi - abs(a - b))
    assert delta < 0.05


def test_talk_catalog_size():
    assert TALK_RHOS == (2.0, 4.0, 8.0)
    assert len(TALK_ANIMATIONS) == 24
    etas = {item[2] for item in TALK_ANIMATIONS}
    assert 0.0 not in etas
    assert {0.5, 3.5, 6.0} <= etas
    general = {
        (model, rho, eta)
        for model, rho, eta in TALK_ANIMATIONS
        if rho in TALK_RHOS
    }
    assert general == {
        (model, rho, eta)
        for model in ("vicsek", "votante")
        for rho in TALK_RHOS
        for eta in (0.5, 3.5, 6.0)
    }
    cluster = {
        (model, rho, eta)
        for model, rho, eta in TALK_ANIMATIONS
        if rho not in TALK_RHOS
    }
    assert cluster == {
        (model, rho, 3.5)
        for model in ("vicsek", "votante")
        for rho in TALK_CLUSTER_RHOS
    }


def test_match_talk_resolves_catalog():
    rows = []
    for i, (model, rho, eta) in enumerate(TALK_ANIMATIONS):
        rows.append(
            {
                "model": model,
                "rho": rho,
                "eta": eta,
                "run_dir": f"run{i}",
            }
        )
    found, missing = match_talk(pd.DataFrame(rows))
    assert missing == []
    assert len(found) == 24
