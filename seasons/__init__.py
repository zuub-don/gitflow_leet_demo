"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__
from seasons import spring, summer

spring.init()
summer.init()

__all__ = ["__version__"]
