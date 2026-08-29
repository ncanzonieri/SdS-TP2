from datetime import datetime

from src.paths import iter_batch_dirs, make_batch, stamp


def test_stamp_format():
    assert stamp(datetime(2026, 8, 27, 22, 15, 30)) == "2026-08-27_221530"


def test_make_batch_and_iter(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "simulation").mkdir()
    batch = make_batch("simulation", root=tmp_path, when=datetime(2026, 1, 1, 0, 0, 0))
    (batch / "vicsek_rho2_eta0_T10_seed1").mkdir()
    found = iter_batch_dirs(tmp_path / "output")
    assert batch in found
