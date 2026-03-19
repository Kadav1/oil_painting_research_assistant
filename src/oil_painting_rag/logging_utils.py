"""
logging_utils.py — Structured logging configuration for the project.

All modules must use get_logger(__name__) rather than print().
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

_configured = False


def configure_logging(
    level: int = logging.INFO,
    fmt: str = _DEFAULT_FORMAT,
    date_fmt: str = _DATE_FORMAT,
    stream: Optional[object] = None,
) -> None:
    """Configure root logger once. Safe to call multiple times."""
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=date_fmt))
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Ensures root logger is configured."""
    configure_logging()
    return logging.getLogger(name)
