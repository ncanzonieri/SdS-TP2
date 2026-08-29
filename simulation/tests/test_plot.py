from unittest.mock import patch

import pandas as pd
import pytest

from src.plot import CLUSTER_RHOS, draw_d_time, draw_g, filter_rhos


def test_filter_rhos_matches_java_n_over_l2():
    frame = pd.DataFrame({"rho": [0.32, 0.16, 0.11, 0.3183, 2.0, 99.0]})
    kept = filter_rhos(frame, list(CLUSTER_RHOS))
    assert sorted(kept["rho"].tolist()) == [0.11, 0.16, 0.3183, 0.32, 2.0]


def _d_index():
    return pd.DataFrame(
        [
            {
                "model": "vicsek",
                "rho": 2.0,
                "eta": 0.0,
                "run_dir": "r1",
            }
        ]
    )


def _d_series():
    return pd.DataFrame({"t": [0, 1, 2, 3], "va": [0.1] * 4, "S": [0.2, 0.3, 0.4, 0.4]})


def _d_onset(*, t_onset_S, status_S):
    return pd.DataFrame(
        [
            {
                "run_dir": "r1",
                "t_onset_va": 1,
                "status_va": "ok",
                "t_onset_S": t_onset_S,
                "status_S": status_S,
            }
        ]
    )


def test_draw_d_time_axvline_uses_usable_onset(tmp_path):
    def load(_row):
        return _d_series()

    with patch("matplotlib.axes.Axes.axvline") as vline:
        draw_d_time(
            _d_index(),
            load,
            _d_onset(t_onset_S=2, status_S="ok"),
            fig_dir=tmp_path,
            compare=False,
        )
    assert vline.called
    assert vline.call_args[0][0] == 2.0
    assert (tmp_path / "fig-d-S-t.png").is_file()


def test_draw_d_time_skips_onset_when_not_usable(tmp_path):
    def load(_row):
        return _d_series()

    with patch("matplotlib.axes.Axes.axvline") as vline:
        draw_d_time(
            _d_index(),
            load,
            _d_onset(t_onset_S=2, status_S="never"),
            fig_dir=tmp_path,
            compare=False,
        )
    vline.assert_not_called()


def test_draw_g_requires_named_tp1_columns(tmp_path):
    tp1 = tmp_path / "tp1.csv"
    tp1.write_text("foo,bar\n1,2\n", encoding="utf-8")
    cim = pd.DataFrame({"N": [10], "mean_ms": [1.0], "stdev_ns": [0.0]})
    with pytest.raises(ValueError, match="missing columns"):
        draw_g(
            [cim],
            fig_dir=tmp_path,
            tp1=tp1,
            tp1_n_col="N",
            tp1_t_col="mean_ms",
        )
