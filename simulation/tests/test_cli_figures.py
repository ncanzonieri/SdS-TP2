import sys
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

from src.cli import (
    _ask_tp1_csv,
    _ask_typed_batch_path,
    _batch_cli_args,
    _build_parser,
    _choose_batch,
    _expand_user_path,
    _generate_assignment_outputs,
    _interactive_outputs,
    _production_args,
    _talk_args,
    interactive,
    main,
)
from src.io import ingest
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
    assert (figs / "fig-c-vicsek.png").is_file()
    assert (figs / "fig-c-votante.png").is_file()
    assert (figs / "fig-c-vicsek.pdf").is_file()
    assert not (figs / "fig-c.png").exists()
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
    assert (bdir / "fig-b-vicsek.png").stat().st_size > 0
    assert not (bdir / "fig-b.png").exists()


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
    assert (figs / "fig-d-S-t-vicsek.png").is_file()
    assert not (figs / "fig-d-S-t.png").exists()


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


def test_animate_format_defaults_to_both():
    ns = _build_parser().parse_args(["animate"])
    assert ns.format == "both"


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
    assert (figs / "fig-c-vicsek.png").is_file()
    assert (figs / "fig-d-S-t-vicsek.png").is_file()
    assert (figs / "fig-d-S-eta-vicsek.png").is_file()
    assert (figs / "fig-e-vicsek.png").is_file()
    assert (figs / "fig-g.png").is_file()


def test_assignment_data_profiles_match_frozen_plan():
    production = _production_args()
    assert production[production.index("--rho") + 1] == "2,4,8"
    assert production[production.index("--eta") + 1] == "0:6:0.5"
    assert production[production.index("--T") + 1] == "500"
    assert production[production.index("--repeats") + 1] == "5"
    assert "--dynamic" not in production

    talk = _talk_args()
    assert talk[talk.index("--rho") + 1] == "2,4,8"
    assert talk[talk.index("--eta") + 1] == "0.5,3.5,6"
    assert "--dynamic" in talk


def test_interactive_menu_has_three_user_facing_workflows():
    with patch("src.cli.questionary.select") as select:
        select.return_value.ask.return_value = None
        assert interactive() == 1
    choices = select.call_args.kwargs["choices"]
    assert [choice.value for choice in choices] == ["data", "results", "all"]


def test_tp1_prompt_asks_yes_or_no_before_requesting_path(tmp_path):
    with (
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
