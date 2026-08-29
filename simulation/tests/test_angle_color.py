import math

import numpy as np
import pandas as pd

from src.animate import TALK_ANIMATIONS, match_talk, theta


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
    assert len(TALK_ANIMATIONS) == 12
    etas = {item[2] for item in TALK_ANIMATIONS}
    assert 0.0 not in etas
    assert {0.5, 3.5, 6.0} <= etas


def test_match_talk_resolves_twelve():
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
    assert len(found) == 12
