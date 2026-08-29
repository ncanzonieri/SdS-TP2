from src.io import (
    fmt,
    format_run_dirname,
    ingest,
    parse_run_dirname,
    read_cim_series,
    read_observables,
    read_static,
    scan_runs,
)
from tests.conftest import FIXTURE_BATCH


def test_fmt_and_roundtrip():
    meta = parse_run_dirname("vicsek_rho2_eta0_T10_seed1")
    assert meta is not None
    assert meta.repeat is None
    assert format_run_dirname(meta) == "vicsek_rho2_eta0_T10_seed1"
    assert fmt(2.0) == "2"
    assert fmt(0.318309886) == "0.3183"
    cluster = parse_run_dirname("vicsek_rho0.3183_eta0.5_T10_seed2_r0")
    assert cluster is not None
    assert cluster.repeat == 0
    assert format_run_dirname(cluster) == "vicsek_rho0.3183_eta0.5_T10_seed2_r0"


def test_repeat_has_distinct_seed():
    a = parse_run_dirname("vicsek_rho2_eta0_T10_seed1")
    b = parse_run_dirname("vicsek_rho2_eta0_T10_seed32_r1")
    assert a is not None and b is not None
    assert a.seed != b.seed
    assert b.repeat == 1


def test_scan_skips_and_loads(tmp_path):
    runs, skips = scan_runs(FIXTURE_BATCH)
    names = {r.path.name for r in runs}
    assert "vicsek_rho2_eta0_T10_seed1" in names
    assert "vicsek_rho2_eta0_T10_seed32_r1" in names
    reasons = " ".join(s.reason for s in skips)
    assert "name does not match" in reasons
    n, L = read_static(FIXTURE_BATCH / "vicsek_rho2_eta0_T10_seed1" / "static.txt")
    assert (n, L) == (4, 10)


def test_observables_and_cim():
    frame = read_observables(FIXTURE_BATCH / "vicsek_rho2_eta0_T10_seed1" / "observables.txt")
    assert list(frame.columns) == ["t", "va", "S"]
    assert len(frame) == 11
    cim = read_cim_series(FIXTURE_BATCH / "cim_times_L20.txt")
    assert "mean_ms" in cim.columns
    assert len(cim) == 3


def test_truncated_raises():
    try:
        read_observables(FIXTURE_BATCH / "vicsek_rho2_eta1_T10_seed9" / "observables.txt")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_scan_single_run_dir():
    run = FIXTURE_BATCH / "vicsek_rho2_eta0_T10_seed1"
    runs, skips = scan_runs(run)
    assert skips == []
    assert len(runs) == 1
    assert runs[0].path == run


def test_n_mismatch_is_warning_not_skip(tmp_path):
    result = ingest(FIXTURE_BATCH, tmp_path)
    assert result.warnings
    assert all("loaded anyway" in msg for msg in result.warnings)
    assert all("loaded anyway" not in s.reason for s in result.skips)
    assert not result.index.empty
