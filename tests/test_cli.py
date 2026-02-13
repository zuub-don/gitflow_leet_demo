"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    for name in ("Spring", "Summer", "Autumn", "Winter"):
        assert name in captured.out


def test_main_info_each_season(capsys):
    for name in ("spring", "summer", "autumn", "winter"):
        ret = main(["info", name])
        assert ret == 0


def test_main_info_unknown(capsys):
    ret = main(["info", "nonexistent"])
    assert ret == 1


def test_main_summary(capsys):
    ret = main(["summary"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Season" in captured.out
    assert "Spring" in captured.out
