import numpy as np
import pandas as pd
import pytest

from src.limits import cover, family_limits, n_min_from, stationary_samples


def test_family_limits_pad_and_cap():
    limits = family_limits([(0.88, "Vicsek ρ=2 η=3.5 en t=381"), (1.0, "Vicsek ρ=8 η=0 ⟨S⟩")], n_min=200)
    assert limits.lo < 0.88
    assert limits.hi > 1.0
    assert limits.hi <= 1.0 + 0.05 * (1.0 - 0.88) + 1e-12
    assert "t=381" in limits.lo_source


def test_resolution_floor_when_almost_flat():
    limits = family_limits([(1.0, "a"), (0.999, "b")], n_min=200)
    assert limits.lo == pytest.approx(0.9995 - 5.0 / 200)
    assert limits.hi == pytest.approx(1.0 + 0.05 * 0.001)


def test_cover_expands_when_a_point_escapes():
    limits = family_limits([(0.95, "in"), (1.0, "hi")], n_min=200)
    widened = cover(limits, np.array([0.80]))
    assert widened.lo <= 0.80
    assert widened.lo < limits.lo


def test_cover_can_pass_the_one_plus_pad_cap():
    limits = family_limits([(0.999, "a"), (1.0, "b")], n_min=200)
    assert limits.hi < 1.01
    widened = cover(limits, np.array([1.01]))
    assert widened.hi >= 1.01


def test_stationary_samples_include_error_bars():
    agg = pd.DataFrame(
        [
            {
                "model": "vicsek",
                "rho": 2.0,
                "eta": 3.5,
                "S_ss": 0.96,
                "S_ss_std": 0.04,
            }
        ]
    )
    values = [value for value, _source in stationary_samples(agg)]
    assert min(values) == pytest.approx(0.92)
    assert max(values) == pytest.approx(1.0)


def test_n_min_from_n_column():
    frame = pd.DataFrame({"N": [200, 400, 800], "rho": [2.0, 4.0, 8.0]})
    assert n_min_from(frame) == 200
