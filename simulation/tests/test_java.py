from pathlib import Path

from src.java import FakeProcess, expand_numeric_list, run_engine


def test_expand_eta_range_to_comma_list():
    # Java is from:to:step (not MATLAB start:step:stop).
    assert expand_numeric_list("0:6:0.5") == (
        "0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6"
    )
    assert expand_numeric_list("0:0.5:6") == "0"
    assert expand_numeric_list("2,4,8") == "2,4,8"


def test_run_engine_expands_colon_range(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "experiment" / "pom.xml").write_text("<project/>", encoding="utf-8")
    (tmp_path / "simulation").mkdir()
    fake = FakeProcess()
    run_engine(
        ["--model", "vicsek", "--eta", "0:6:0.5"],
        out_dir=tmp_path / "o",
        process=fake,
        root=tmp_path,
    )
    joined = fake.calls[0][0][-1]
    assert "0:6:0.5" not in joined
    assert "0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6" in joined


def test_injects_absolute_out(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "experiment" / "pom.xml").write_text("<project/>", encoding="utf-8")
    (tmp_path / "simulation").mkdir()
    fake = FakeProcess()
    out = tmp_path / "output" / "simulation" / "batch1"
    result = run_engine(["--model", "vicsek"], out_dir=out, process=fake, root=tmp_path)
    assert result == out
    argv, cwd = fake.calls[0]
    assert cwd == tmp_path
    assert argv[0] == "mvn"
    assert argv[argv.index("clean") : argv.index("exec:java") + 1] == [
        "clean",
        "compile",
        "exec:java",
    ]
    joined = " ".join(argv)
    assert "--out" in joined
    assert str(out.resolve()) in joined


def test_user_out_wins(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "experiment" / "pom.xml").write_text("<project/>", encoding="utf-8")
    (tmp_path / "simulation").mkdir()
    fake = FakeProcess()
    custom = tmp_path / "custom"
    run_engine(["--out", str(custom), "--cim-benchmark"], process=fake, root=tmp_path)
    argv, _cwd = fake.calls[0]
    assert argv[-1].endswith(str(custom)) or str(custom) in argv[-1]


def test_nonzero_status_raises(tmp_path):
    (tmp_path / "experiment").mkdir()
    (tmp_path / "experiment" / "pom.xml").write_text("<project/>", encoding="utf-8")
    (tmp_path / "simulation").mkdir()
    fake = FakeProcess(returncode=1)
    try:
        run_engine(["--help"], out_dir=tmp_path / "o", process=fake, root=tmp_path)
    except RuntimeError as exc:
        assert "status 1" in str(exc)
        return
    raise AssertionError("expected RuntimeError")
