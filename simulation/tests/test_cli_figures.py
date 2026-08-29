from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

from src.cli import _build_parser, main
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
    assert (figs / "fig-c.png").is_file()
    assert (figs / "fig-c.pdf").is_file()
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
    assert (bdir / "fig-b.png").stat().st_size > 0


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
    assert (figs / "fig-d-S-t.png").is_file()


def test_ingest_does_not_cache_onset(tmp_path):
    cache = tmp_path / "cache"
    ingest(FIXTURE_BATCH, cache)
    names = {p.name for p in cache.iterdir()}
    assert "index.csv.gz" in names
    assert "onset.csv.gz" not in names
    assert "agg.csv.gz" not in names


def test_animate_without_ffmpeg(tmp_path):
    cache = tmp_path / "cache"
    ingest(FIXTURE_BATCH, cache)
    with patch("src.animate.shutil.which", return_value=None):
        code = main(
            [
                "animate",
                "--run-dir",
                "vicsek_rho2_eta0_T10_seed1",
                "--out",
                str(FIXTURE_BATCH),
                "--cache-dir",
                str(cache),
            ]
        )
    assert code == 1


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
    assert (figs / "fig-b.png").is_file()
    assert (figs / "fig-c.png").is_file()
    assert (figs / "fig-d-S-t.png").is_file()
    assert (figs / "fig-d-S-eta.png").is_file()
    assert (figs / "fig-e.png").is_file()
    assert (figs / "fig-g.png").is_file()
