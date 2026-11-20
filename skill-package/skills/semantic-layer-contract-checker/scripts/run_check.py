#!/usr/bin/env python3
"""Run the bundled Semantic Layer Contract Checker.

Usage mirrors the contractcheck CLI:
    python3 run_check.py check --platform dbt --input path/to/manifest.json --format md --out scorecard.md
    python3 run_check.py check --platform promptql --input path/to/metadata/ --format html --out scorecard.html
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "checker"))

from contractcheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
