#!/usr/bin/env python
"""Backward-compatible wrapper for the packaged AggreQuant CLI."""

from aggrequant.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
