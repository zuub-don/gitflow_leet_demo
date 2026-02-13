"""EXPERIMENTAL: This file was accidentally committed directly to main.

This simulates a junior developer pushing directly to the production branch
instead of creating a feature branch. This should NEVER happen in Git Flow.
"""

def untested_function():
    """This function has no tests and was never reviewed."""
    print("YOLO deploying to production!")
    return 42 / 0  # This will crash at runtime
