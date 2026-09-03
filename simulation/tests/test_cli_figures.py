import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import matplotlib

matplotlib.use("Agg")

from argparse import Namespace

from src.cli import (
    _ask_tp1_csv,
    _ask_typed_batch_path,
    _batch_cli_args,
    _build_parser,
    _choose_batch,
    _expand_user_path,
    _scan_root,
    _generate_assignment_outputs,
    _interactive_outputs,
    _production_args,
    _production_run_counts,
    _talk_args,
    _talk_run_count,
    interactive,
    main,
)
from src.io import ingest
from src.limits import compute_s_limits
from tests.conftest import FIXTURE_BATCH


def test_fig_c_and_b_write_files(tmp_path):
    cache = tmp_path / "cache"
    figs = tmp_path / "figs"
    ingest(FIXTURE_BATCH, cache)
    assert main(
        [
            "fig-c",
            "--out",
            str(FIXTURE_BATCH),
            "--cache-dir",
            str(cache),
            "--fig-dir",
            str(figs),
            "--window",
            "3",
            "--t-min",
            "0",
            "--sustain",
            "1",
        ]
    ) == 0
    assert (figs / "c_va_vs_eta_vicsek.png").is_file()
    assert (figs / "c_va_vs_eta_votante.png").is_file()
    # Las tablas del estacionario acompanan a las figuras (no van a output/data
    # cuando se pide --fig-dir).
    assert (figs / "estacionario_por_corrida.csv").is_file()
    assert (figs / "estacionario_promedios.csv").is_file()
    assert not (figs / "c_va_vs_eta_vicsek.pdf").exists()
    assert not (figs / "c_va_vs_eta.png").exists()
    compared = tmp_path / "figs-compare"
    assert main(
        [
            "fig-c",
            "--out",
            str(FIXTURE_BATCH),
            "--cache-dir",
            str(cache),
            "--fig-dir",
            str(compared),
            "--window",
            "3",
            "--t-min",
            "0",
            "--sustain",
            "1",
            "--compare",
        ]
    ) == 0
    assert (compared / "f_va_vs_eta.png").is_file()
    assert (compared / "c_va_vs_eta_vicsek.png").is_file()
    assert (compared / "c_va_vs_eta_votante.png").is_file()
    bdir = tmp_path / "figb"
    assert main(
        [
            "fig-b",
            "--out",
            str(FIXTURE_BATCH),
            "--cache-dir",
            str(cache),
            "--fig-dir",
            str(bdir),
            "--window",
            "3",
            "--t-min",
            "0",
            "--sustain",
            "1",
            "--series",
            "va",
        ]
    ) == 0
    assert (bdir / "b_va_t_vicsek.png").stat().st_size > 0
    assert not (bdir / "f_va_t.png").exists()


def test_fig_d_time_without_rho(tmp_path):
    cache = tmp_path / "cache"
    figs = tmp_path / "figd"
    ingest(FIXTURE_BATCH, cache)
    assert main(
        [
            "fig-d",
            "--panel",
            "time",
            "--out",
            str(FIXTURE_BATCH),
            "--cache-dir",
            str(cache),
            "--fig-dir",
            str(figs),
            "--window",
            "3",
            "--t-min",
            "0",
            "--sustain",
            "1",
        ]
    ) == 0
    assert (figs / "d_S_t_vicsek.png").is_file()
    assert not (figs / "d_S_t.png").exists()


def test_ingest_does_not_cache_onset(tmp_path):
    cache = tmp_path / "cache"
    ingest(FIXTURE_BATCH, cache)
    names = {p.name for p in cache.iterdir()}
    assert "index.csv.gz" in names
    assert "onset.csv.gz" not in names
    assert "agg.csv.gz" not in names


def test_animate_uses_gif_destination(tmp_path):
    cache = tmp_path / "cache"
    ingest(FIXTURE_BATCH, cache)
    expected = tmp_path / "flock.gif"
    with patch("src.cli.animate_run", return_value=(expected,)) as animate:
        code = main(
            [
                "animate",
                "--format",
                "gif",
                "--run-dir",
                "vicsek_rho2_eta0_T10_seed1",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
            ]
        )
    assert code == 0
    assert animate.call_args.kwargs["dest"].name == "flock"
    assert animate.call_args.kwargs["opts"].output_format == "gif"


def test_animate_rho_and_runs_are_applied(tmp_path):
    cache = tmp_path / "cache"
    ingest(FIXTURE_BATCH, cache)
    with patch("src.cli._animate", return_value=0) as anim:
        code = main(
            [
                "animate",
                "--anim",
                "gif",
                "--rho",
                "4",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
            ]
        )
    assert code == 0
    index = anim.call_args[0][0]
    assert set(index["rho"].astype(float)) == {4.0}

    with patch("src.cli._animate", return_value=0) as anim:
        code = main(
            [
                "animate",
                "--anim",
                "gif",
                "--runs",
                "vicsek_rho2_eta0_T10_seed1",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
            ]
        )
    assert code == 0
    index = anim.call_args[0][0]
    assert list(index["run_dir"]) == ["vicsek_rho2_eta0_T10_seed1"]


def test_fig_g_parser_has_no_steady_flags():
    ns = _build_parser().parse_args(["fig-g"])
    assert not hasattr(ns, "window")
    assert not hasattr(ns, "atol")
    assert ns.tp1 is None


def test_invalid_figs_value_is_rejected():
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["fig-c", "--figs", "jpeg"])


def test_figs_both_writes_pdf(tmp_path):
    cache = tmp_path / "cache"
    figs = tmp_path / "figs"
    ingest(FIXTURE_BATCH, cache)
    assert (
        main(
            [
                "fig-c",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
                "--fig-dir",
                str(figs),
                "--figs",
                "both",
                "--window",
                "3",
                "--t-min",
                "0",
                "--sustain",
                "1",
            ]
        )
        == 0
    )
    assert (figs / "c_va_vs_eta_vicsek.png").is_file()
    assert (figs / "c_va_vs_eta_vicsek.pdf").is_file()


def test_animate_defaults_skip_animations():
    ns = _build_parser().parse_args(["animate"])
    assert ns.anim == "none"
    assert ns.format is None
    assert ns.figs == "png"


def test_anim_none_skips_without_reading_positions(tmp_path):
    with patch("src.cli._animate") as animate, patch("src.cli._load_index") as load:
        assert main(["animate", "--out", str(FIXTURE_BATCH), "--cache-dir", str(tmp_path)]) == 0
    animate.assert_not_called()
    load.assert_not_called()


def test_explicit_anim_none_wins_over_format_alias(tmp_path):
    with patch("src.cli._animate") as animate, patch("src.cli._load_index") as load:
        assert (
            main(
                [
                    "animate",
                    "--anim",
                    "none",
                    "--format",
                    "gif",
                    "--out",
                    str(FIXTURE_BATCH),
                    "--cache-dir",
                    str(tmp_path),
                ]
            )
            == 0
        )
    animate.assert_not_called()
    load.assert_not_called()


def test_fig_b_limits_use_the_full_index_not_the_b_slice(tmp_path):
    cache = tmp_path / "cache"
    figs = tmp_path / "figs"
    ingest(FIXTURE_BATCH, cache)
    with patch("src.cli.compute_s_limits", wraps=compute_s_limits) as compute:
        assert (
            main(
                [
                    "fig-b",
                    "--out",
                    str(FIXTURE_BATCH),
                    "--cache-dir",
                    str(cache),
                    "--fig-dir",
                    str(figs),
                    "--window",
                    "3",
                    "--t-min",
                    "0",
                    "--sustain",
                    "1",
                    "--series",
                    "va",
                ]
            )
            == 0
        )
    index = compute.call_args[0][0]
    assert len(index) > 1
    assert {float(rho) for rho in index["rho"]} != {4.0}


def test_cmd_all_shares_prepare_path(tmp_path):
    cache = tmp_path / "cache"
    figs = tmp_path / "figs"
    assert (
        main(
            [
                "all",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
                "--fig-dir",
                str(figs),
                "--window",
                "3",
                "--t-min",
                "0",
                "--sustain",
                "1",
            ]
        )
        == 0
    )
    assert (figs / "c_va_vs_eta_vicsek.png").is_file()
    assert (figs / "d_S_t_vicsek.png").is_file()
    assert (figs / "d_S_vs_eta_vicsek.png").is_file()
    assert (figs / "e_va_vs_S_vicsek.png").is_file()
    assert (figs / "g_cim_times.png").is_file()


def test_assignment_data_profiles_cover_both_density_families():
    """El barrido va en dos tandas porque `--repeats` es global en Java.

    Las densidades bajas del estudio de clusters (N entre 11 y 32) necesitan mas
    realizaciones que las tres del enunciado.
    """
    (_, general), (_, low) = _production_args()
    assert general[general.index("--rho") + 1] == "2,4,8"
    assert general[general.index("--repeats") + 1] == "5"
    assert low[low.index("--rho") + 1] == "0.1061,0.1592,0.3183"
    assert low[low.index("--repeats") + 1] == "20"
    for args in (general, low):
        assert args[args.index("--eta") + 1] == "0:6:0.5"
        assert "--dynamic" not in args
    assert general[general.index("--T") + 1] == "10000"
    # N=11..32: S(t) tiene tiempos de correlacion ~10^3 pasos; T=2000 no alcanza.
    assert low[low.index("--T") + 1] == "10000"
    assert _production_run_counts() == (390, 1560)

    talk_general, talk_low = _talk_args()
    assert talk_general[talk_general.index("--rho") + 1] == "2,4,8"
    assert talk_general[talk_general.index("--eta") + 1] == "0.5,3.5,6"
    assert talk_low[talk_low.index("--rho") + 1] == "0.1061,0.1592,0.3183"
    assert talk_low[talk_low.index("--eta") + 1] == "3.5"
    for args in (talk_general, talk_low):
        assert "--dynamic" in args
    assert _talk_run_count() == 24


def test_interactive_menu_has_three_user_facing_workflows():
    with patch("src.cli.questionary.select") as select:
        select.return_value.ask.return_value = None
        assert interactive() == 1
    choices = select.call_args.kwargs["choices"]
    assert [choice.value for choice in choices] == ["data", "results", "all"]


def test_tp1_prompt_asks_yes_or_no_before_requesting_path(tmp_path):
    # Sin CSV del TP1 en simulation/tp1 el asistente pregunta; con el CSV
    # cargado (caso real del repo) lo usa directo, por eso se anula aca.
    with (
        patch("src.cli.default_tp1_csv", return_value=None),
        patch("src.cli.questionary.confirm") as confirm,
        patch("src.cli.questionary.text") as text,
    ):
        confirm.return_value.ask.return_value = False
        assert _ask_tp1_csv() is None
        text.assert_not_called()

        tp1 = tmp_path / "tp1.csv"
        tp1.write_text("N,mean_ms\n10,1\n", encoding="utf-8")
        confirm.return_value.ask.return_value = True
        text.return_value.ask.return_value = str(tp1)
        assert _ask_tp1_csv() == tp1


def test_assignment_outputs_cover_points_a_to_g(tmp_path):
    tp1 = tmp_path / "tp1.csv"
    tp1.write_text("N,mean_ms\n1,1\n", encoding="utf-8")
    with (
        patch("src.cli.make_batch", return_value=tmp_path / "figures"),
        patch("src.cli.main", return_value=0) as dispatch,
    ):
        assert (
            _generate_assignment_outputs(
                "analysis-batch",
                "animation-batch",
                "cim-batch",
                tp1=tp1,
            )
            == 0
        )

    calls = [call.args[0] for call in dispatch.call_args_list]
    assert [argv[0] for argv in calls] == [
        "time-series",
        "polarization-vs-noise",
        "clusters",
        "polarization-vs-cluster",
        "animation",
        "cim-comparison",
    ]
    assert all("--compare" in argv for argv in calls[:4])
    assert calls[4][calls[4].index("--batch") + 1] == "animation-batch"
    assert "--talk" in calls[4]
    assert calls[5][calls[5].index("--batch") + 1] == "cim-batch"
    assert calls[5][calls[5].index("--tp1") + 1] == str(tp1)


def test_interactive_outputs_overlay_no_omits_compare():
    with (
        patch("src.cli.questionary.checkbox") as checkbox,
        patch("src.cli.questionary.confirm") as confirm,
        patch("src.cli._choose_batch", return_value="analysis-batch"),
        patch("src.cli.main", return_value=0) as dispatch,
    ):
        checkbox.return_value.ask.return_value = [
            "time-series",
            "polarization-vs-noise",
            "clusters",
            "polarization-vs-cluster",
        ]
        confirm.return_value.ask.return_value = False
        assert _interactive_outputs() == 0
    calls = [call.args[0] for call in dispatch.call_args_list]
    assert [argv[0] for argv in calls] == [
        "time-series",
        "polarization-vs-noise",
        "clusters",
        "polarization-vs-cluster",
    ]
    assert all("--compare" not in argv for argv in calls)


def test_batch_cli_args_dir_uses_out_else_batch(tmp_path):
    assert _batch_cli_args(tmp_path) == ["--out", str(tmp_path.resolve())]
    assert _batch_cli_args("analysis-batch") == ["--batch", "analysis-batch"]


def test_scan_root_absolute_batch_is_out(tmp_path):
    assert _scan_root(Namespace(out=None, batch=str(tmp_path))) == tmp_path.resolve()


def test_scan_root_batch_name_stays_under_output_simulation():
    path = _scan_root(Namespace(out=None, batch="2026-09-02_201710"))
    assert path.name == "2026-09-02_201710"
    assert path.parent.name == "simulation"


def test_choose_batch_last_choice_writes_a_path(tmp_path):
    def pick_write_path(prompt, choices):
        assert choices[-1].title == "Escribir un path..."

        class _Ask:
            def ask(self_inner):
                return choices[-1].value

        return _Ask()

    with (
        patch("src.cli._batch_dirs", return_value=[]),
        patch("src.cli.questionary.select", side_effect=pick_write_path),
        patch("src.cli.questionary.text") as text,
    ):
        text.return_value.ask.return_value = str(tmp_path)
        assert _choose_batch() == tmp_path.resolve()


def test_ask_typed_batch_path_retries_invalid(tmp_path, capsys):
    good = tmp_path / "lote"
    good.mkdir()
    answers = iter([str(tmp_path / "missing"), "y", str(good)])
    with patch("src.cli.questionary.text") as text:
        text.return_value.ask.side_effect = lambda: next(answers)
        assert _ask_typed_batch_path() == good.resolve()
    err = capsys.readouterr().err
    assert err.count("error:") >= 2


def test_expand_user_path_maps_wsl_prefix_on_windows():
    path = _expand_user_path("/mnt/d/lote")
    if sys.platform == "win32":
        assert path.drive.lower() == "d:"
        assert path.name == "lote"
    else:
        assert path == Path("/mnt/d/lote")
