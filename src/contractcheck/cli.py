"""Command line interface.

Usage:
  contractcheck check --platform dbt --input path/to/manifest.json \
      --format md --out scorecard.md
  contractcheck check --platform promptql --input path/to/metadata/ \
      --format html --out scorecard.html
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import engine, report
from .adapters import dbt as dbt_adapter
from .adapters import promptql as promptql_adapter

ADAPTERS = {"dbt": dbt_adapter, "promptql": promptql_adapter}
RENDERERS = {"md": report.render_markdown, "html": report.render_html,
             "json": report.render_json}
EXTENSIONS = {"md": ".md", "html": ".html", "json": ".json"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contractcheck",
        description="Audit a semantic-layer project against the "
                    "machine-consumption contract (R1 to R10).")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Score a project and write a scorecard.")
    check.add_argument("--platform", choices=sorted(ADAPTERS), required=True)
    check.add_argument("--input", required=True,
                       help="dbt: manifest.json file or project directory. "
                            "promptql: metadata directory.")
    check.add_argument("--format", choices=sorted(RENDERERS), default="md")
    check.add_argument("--out", default=None,
                       help="Output file (default: scorecard.<ext> in the "
                            "current directory).")
    check.add_argument("--strict", action="store_true",
                       help="Exit 1 if any requirement is coded "
                            "'not documented' (for CI use).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    adapter = ADAPTERS[args.platform]
    try:
        project = adapter.load_project(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    scorecard = engine.score_project(project)
    out = Path(args.out) if args.out else Path(f"scorecard{EXTENSIONS[args.format]}")
    out.write_text(RENDERERS[args.format](scorecard), encoding="utf-8")
    print(report.summary_line(scorecard))
    for cell in scorecard.cells:
        print(f"  {cell.requirement} {cell.title}: {cell.verdict}")
    print(f"Scorecard written to {out}")
    if args.strict and scorecard.counts()[engine.NOT_DOCUMENTED]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
