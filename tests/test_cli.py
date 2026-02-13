"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "seasons" in captured.out.lower()


def test_main_info_missing(capsys):
    ret = main(["info", "spring"])
    assert ret == 1
