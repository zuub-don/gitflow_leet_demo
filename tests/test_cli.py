"""Tests for the CLI module."""
from seasons.cli import main


def test_main_no_args(capsys):
    ret = main([])
    assert ret == 0


def test_main_all(capsys):
    ret = main(["all"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Spring" in captured.out


def test_main_info_spring(capsys):
    ret = main(["info", "spring"])
    captured = capsys.readouterr()
    assert ret == 0
    assert "Spring" in captured.out
    assert "March" in captured.out


def test_main_info_unknown(capsys):
    ret = main(["info", "nonexistent"])
    assert ret == 1
