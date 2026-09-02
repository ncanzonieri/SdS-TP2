from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.paths import (
    POINT_FOLDERS,
    ensure_dir,
    iter_batch_dirs,
    make_batch,
    point_dir,
    resolve_scan_root,
    stamp,
    windows_path,
)


def test_stamp_format():
    assert stamp(datetime(2026, 8, 27, 22, 15, 30)) == "2026-08-27_221530"


def test_make_batch_and_iter(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "simulation").mkdir()
    batch = make_batch("simulation", root=tmp_path, when=datetime(2026, 1, 1, 0, 0, 0))
    (batch / "vicsek_rho2_eta0_T10_seed1").mkdir()
    found = iter_batch_dirs(tmp_path / "output")
    assert batch in found


def test_resolve_scan_root_name_vs_absolute(tmp_path):
    named = resolve_scan_root(batch="2026-09-02_201710", root=tmp_path)
    assert named == tmp_path / "output" / "simulation" / "2026-09-02_201710"
    assert resolve_scan_root(out=tmp_path / "lote", root=tmp_path) == tmp_path / "lote"
    assert resolve_scan_root(batch=str(tmp_path / "lote"), root=tmp_path) == tmp_path / "lote"
    # A name that also exists as a cwd/package folder stays a batch name.
    assert resolve_scan_root(batch="simulation", root=tmp_path) == tmp_path / "output" / "simulation" / "simulation"


def test_windows_path_from_wsl_mnt():
    with patch("src.paths.shutil.which", return_value=None):
        assert windows_path(Path("/mnt/c/Users/x/output")) == r"C:\Users\x\output"
        assert windows_path(Path("/mnt/d/data")) == r"D:\data"
        assert windows_path(Path("/home/fede/out")) is None


def test_point_dir_uses_assignment_names(tmp_path):
    dest = point_dir("d", root=tmp_path)
    assert dest == tmp_path / "output" / POINT_FOLDERS["d"]
    assert dest.is_dir()


def test_ensure_dir_creates_and_is_idempotent(tmp_path):
    dest = tmp_path / "output" / "simulation" / "batch"
    assert ensure_dir(dest) == dest
    assert dest.is_dir()
    assert ensure_dir(dest) == dest


def test_ensure_dir_replaces_a_file(tmp_path):
    dest = tmp_path / "output"
    dest.write_text("not a directory", encoding="utf-8")
    ensure_dir(dest)
    assert dest.is_dir()


def test_ensure_dir_uses_windows_mkdir_on_wsl_ghost(tmp_path):
    dest = tmp_path / "output"
    real_mkdir = Path.mkdir

    def boom(self, *args, **kwargs):
        raise FileExistsError(17, "File exists", str(self))

    def fake_win(path: Path) -> bool:
        real_mkdir(path, parents=True, exist_ok=True)
        return path.is_dir()

    with patch.object(Path, "mkdir", boom), patch("src.paths._mkdir_via_windows", side_effect=fake_win):
        assert ensure_dir(dest) == dest
        assert dest.is_dir()


def test_ensure_dir_errors_when_windows_fallback_fails(tmp_path):
    dest = tmp_path / "output"

    def boom(self, *args, **kwargs):
        raise FileExistsError(17, "File exists", str(self))

    with (
        patch.object(Path, "mkdir", boom),
        patch("src.paths._mkdir_via_windows", return_value=False),
        pytest.raises(FileExistsError, match="not a usable directory"),
    ):
        ensure_dir(dest)
