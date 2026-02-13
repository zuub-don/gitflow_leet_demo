"""Seasons — a CLI tool for seasonal information."""
from seasons.__version__ import __version__
from seasons import spring, summer, autumn, winter

spring.init()
summer.init()
autumn.init()
winter.init()

__all__ = ["__version__"]
