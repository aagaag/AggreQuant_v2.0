"""Command-line interface for the AggreQuant segmentation pipeline."""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser without importing optional pipeline dependencies."""
    parser = argparse.ArgumentParser(
        prog="aggrequant",
        description="Run the AggreQuant segmentation pipeline from a YAML configuration file",
    )
    parser.add_argument("config", type=Path, help="Path to the YAML configuration file")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output",
    )
    parser.add_argument(
        "--max-fields",
        type=int,
        default=None,
        help="Stop after processing this many fields (for quick testing)",
    )
    parser.add_argument(
        "--segmentation-only",
        action="store_true",
        help="Only run segmentation (skip quantification, CSV output, and plots)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the pipeline and return a process exit status."""
    args = build_parser().parse_args(argv)

    if not args.config.is_file():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        return 1

    # Keep the import lazy so ``aggrequant --help`` works even when the
    # optional segmentation dependencies have not been installed.
    from aggrequant.pipeline import SegmentationPipeline

    try:
        print(f"Loading configuration from {args.config}")
        pipeline = SegmentationPipeline(config_path=args.config, verbose=args.verbose)
        pipeline.run(
            max_fields=args.max_fields,
            segmentation_only=args.segmentation_only,
        )
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
