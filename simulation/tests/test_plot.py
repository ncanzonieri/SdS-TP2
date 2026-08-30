from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from src.plot import (
    CLUSTER_RHOS,
    VA_YLIM,
    draw_b,
    draw_c,
    draw_d_eta,
    draw_d_time,
    draw_e,
    draw_g,
    filter_rhos,
    save as real_save,
    select_fig_b_runs,
    set_fig_formats,
)


def test_cluster_figures_default_to_assignment_densities():
    frame = pd.DataFrame({"rho": [0.32, 0.16, 0.11, 0.3183, 2.0, 99.0]})
    kept = filter_rhos(frame, list(CLUSTER_RHOS))
    assert CLUSTER_RHOS == (2.0, 4.0, 8.0)
    assert kept["rho"].tolist() == [2.0]


def test_fig_b_selects_one_low_mid_high_run_per_model():
    rows = []
    for model in ("vicsek", "votante"):
        for eta in (0.0, 0.5, 3.5, 6.0):
            for seed in (1, 32):
                rows.append(
                    {
                        "model": model,
                        "rho": 4.0,
                        "eta": eta,
                        "seed": seed,
                        "run_dir": f"{model}-{eta}-{seed}",
                    }
                )
    chosen = select_fig_b_runs(pd.DataFrame(rows))
    assert len(chosen) == 6
    assert set(chosen["eta"]) == {0.5, 3.5, 6.0}
    assert set(chosen["seed"]) == {1}


def _d_index():
    return pd.DataFrame(
        [
            {
                "model": "vicsek",
                "rho": 2.0,
                "eta": 0.0,
                "seed": 1,
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


def _agg(*rows):
    return pd.DataFrame(
        list(rows),
        columns=[
            "model",
            "rho",
            "eta",
            "va_ss",
            "va_ss_err",
            "n_runs_va",
            "S_ss",
            "S_ss_err",
            "n_runs_S",
        ],
    )


def _agg_both_models():
    return _agg(
        ("vicsek", 2.0, 0.5, 0.8, 0.01, 2, 0.7, 0.02, 2),
        ("vicsek", 4.0, 0.5, 0.7, 0.01, 2, 0.6, 0.02, 2),
        ("votante", 2.0, 0.5, 0.5, 0.01, 2, 0.4, 0.02, 2),
    )


def _titles_while(draw):
    titles = []

    def capturing_save(fig, stem):
        titles.extend(ax.get_title() for ax in fig.axes)
        real_save(fig, stem)

    with patch("src.plot.save", side_effect=capturing_save):
        draw()
    return titles


def test_delivery_figures_have_empty_titles(tmp_path):
    def load(_row):
        return _d_series()

    onset = _d_onset(t_onset_S=2, status_S="ok")
    agg = _agg_both_models()
    cim = pd.DataFrame({"N": [10], "mean_ms": [1.0], "stdev_ns": [0.0]})

    titles = _titles_while(
        lambda: (
            draw_b(
                _d_index(),
                load,
                onset,
                series="va",
                fig_dir=tmp_path / "b",
                compare=False,
            ),
            draw_c(agg, fig_dir=tmp_path / "c"),
            draw_d_time(
                _d_index(),
                load,
                onset,
                fig_dir=tmp_path / "d",
                compare=False,
            ),
            draw_e(agg, fig_dir=tmp_path / "e"),
            draw_g(
                [cim],
                fig_dir=tmp_path / "g",
                tp1=None,
                tp1_n_col="N",
                tp1_t_col="mean_ms",
            ),
        )
    )
    assert titles
    assert all(title == "" for title in titles)


def test_draw_c_writes_per_model_stems_never_mixed(tmp_path):
    draw_c(_agg_both_models(), fig_dir=tmp_path)
    stems = {path.stem for path in tmp_path.glob("c_va_vs_eta*")}
    assert "c_va_vs_eta_vicsek" in stems
    assert "c_va_vs_eta_votante" in stems
    assert "c_va_vs_eta" not in stems
    assert not (tmp_path / "c_va_vs_eta.png").exists()
    assert not (tmp_path / "f_va_vs_eta.png").exists()


def test_draw_c_writes_singles_when_multiple_rhos(tmp_path):
    draw_c(_agg_both_models(), fig_dir=tmp_path)
    assert (tmp_path / "c_va_vs_eta_vicsek_rho2.png").is_file()
    assert (tmp_path / "c_va_vs_eta_vicsek_rho4.png").is_file()


def test_draw_d_time_axvline_uses_usable_onset(tmp_path):
    def load(_row):
        return _d_series()

    with patch("matplotlib.axes.Axes.axvline") as vline:
        stems = draw_d_time(
            _d_index(),
            load,
            _d_onset(t_onset_S=2, status_S="ok"),
            fig_dir=tmp_path,
            compare=False,
        )
    assert isinstance(stems, list)
    assert vline.called
    assert vline.call_args[0][0] == 2.0
    assert (tmp_path / "d_S_t_vicsek.png").is_file()
    assert not (tmp_path / "d_S_t.png").exists()
    assert not (tmp_path / "f_S_t.png").exists()


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


def test_save_keeps_decimal_eta_in_filename(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    set_fig_formats("both")
    stem = tmp_path / "b_va_t_vicsek_rho4_eta0.5"
    real_save(fig, stem)
    assert (tmp_path / "b_va_t_vicsek_rho4_eta0.5.png").is_file()
    assert (tmp_path / "b_va_t_vicsek_rho4_eta0.5.pdf").is_file()
    assert not (tmp_path / "b_va_t_vicsek_rho4_eta0.png").exists()
    set_fig_formats("png")


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


def _axes_while(draw):
    axes = []

    def capturing_save(fig, stem):
        axes.extend(fig.axes)
        real_save(fig, stem)

    with patch("src.plot.save", side_effect=capturing_save):
        draw()
    return axes


def _plot_axes(axes):
    return [ax for ax in axes if ax.get_xlabel()]


def _eta_grid_agg():
    return _agg(
        ("vicsek", 2.0, 0.0, 0.95, 0.01, 2, 0.96, 0.01, 2),
        ("vicsek", 2.0, 0.5, 0.80, 0.01, 2, 0.97, 0.01, 2),
        ("vicsek", 2.0, 3.5, 0.40, 0.01, 2, 0.98, 0.01, 2),
        ("vicsek", 2.0, 6.0, 0.10, 0.01, 2, 0.99, 0.01, 2),
        ("votante", 2.0, 0.0, 0.70, 0.01, 2, 0.95, 0.01, 2),
        ("votante", 2.0, 6.0, 0.05, 0.01, 2, 0.94, 0.01, 2),
    )


def test_draw_c_compare_writes_overlay_and_per_model(tmp_path):
    draw_c(_agg_both_models(), fig_dir=tmp_path, compare=True, compare_dir=tmp_path)
    assert (tmp_path / "f_va_vs_eta.png").is_file()
    assert (tmp_path / "c_va_vs_eta_vicsek.png").is_file()
    assert (tmp_path / "c_va_vs_eta_votante.png").is_file()


def test_draw_d_eta_compare_writes_overlay_and_per_model(tmp_path):
    draw_d_eta(_agg_both_models(), fig_dir=tmp_path, compare=True, compare_dir=tmp_path)
    assert (tmp_path / "f_S_vs_eta.png").is_file()
    assert (tmp_path / "d_S_vs_eta_vicsek.png").is_file()
    assert (tmp_path / "d_S_vs_eta_votante.png").is_file()


def test_draw_d_time_compare_writes_overlay_and_per_model(tmp_path):
    def load(_row):
        return _d_series()

    draw_d_time(
        _d_index(),
        load,
        _d_onset(t_onset_S=2, status_S="ok"),
        fig_dir=tmp_path,
        compare=True,
        compare_dir=tmp_path,
    )
    assert (tmp_path / "f_S_t.png").is_file()
    assert (tmp_path / "d_S_t_vicsek.png").is_file()


def test_draw_e_compare_writes_overlay_and_per_model(tmp_path):
    draw_e(_agg_both_models(), fig_dir=tmp_path, compare=True, compare_dir=tmp_path)
    assert (tmp_path / "f_va_vs_S.png").is_file()
    assert (tmp_path / "e_va_vs_S_vicsek.png").is_file()
    assert (tmp_path / "e_va_vs_S_votante.png").is_file()
    assert not (tmp_path / "f_va_vs_S.png").stat().st_size == 0


def test_draw_e_is_scatter_without_polyline(tmp_path):
    axes = _axes_while(lambda: draw_e(_eta_grid_agg(), fig_dir=tmp_path, compare=True))
    for ax in _plot_axes(axes):
        for line in ax.get_lines():
            style = str(line.get_linestyle()).lower()
            if style in {"none", ""}:
                continue
            x = np.asarray(line.get_xdata(), dtype=float)
            y = np.asarray(line.get_ydata(), dtype=float)
            if x.size >= 2 and not np.allclose(x, x[0]) and not np.allclose(y, y[0]):
                pytest.fail("fig-e must not connect (S, va) points with a polyline")


def test_draw_e_uses_data_xlim_and_va_ylim(tmp_path):
    axes = _axes_while(lambda: draw_e(_eta_grid_agg(), fig_dir=tmp_path, compare=False))
    for ax in _plot_axes(axes):
        lo, hi = ax.get_xlim()
        assert lo <= 0.94
        assert hi >= 0.99
        assert ax.get_ylim() == pytest.approx(VA_YLIM)
        assert not any(text.get_text().startswith(r"$\eta") for text in ax.texts)


def test_draw_d_s_panels_follow_data_not_a_fixed_zoom(tmp_path):
    def load(_row):
        return _d_series()

    time_axes = _axes_while(
        lambda: draw_d_time(
            _d_index(),
            load,
            _d_onset(t_onset_S=2, status_S="ok"),
            fig_dir=tmp_path / "t",
            compare=False,
        )
    )
    for ax in _plot_axes(time_axes):
        lo, hi = ax.get_ylim()
        assert lo <= 0.2
        assert hi >= 0.4
        assert hi - lo > 0.1

    eta_axes = _axes_while(
        lambda: draw_d_eta(_agg_both_models(), fig_dir=tmp_path / "eta", compare=False)
    )
    for ax in _plot_axes(eta_axes):
        lo, hi = ax.get_ylim()
        assert lo <= 0.4
        assert hi >= 0.7


def test_errorbar_curves_use_filled_vicsek_and_empty_votante(tmp_path):
    axes = _axes_while(lambda: draw_c(_agg_both_models(), fig_dir=tmp_path, compare=True))
    seen = {"vicsek": False, "votante": False}
    for ax in _plot_axes(axes):
        for line in ax.get_lines():
            label = line.get_label() or ""
            if label.startswith("_") or line.get_marker() in {None, "None", ""}:
                continue
            facecolor = line.get_markerfacecolor()
            if "Vicsek" in label:
                seen["vicsek"] = True
                assert facecolor != "none"
            if "Votante" in label:
                seen["votante"] = True
                assert facecolor == "none"
    assert seen["vicsek"] and seen["votante"]
