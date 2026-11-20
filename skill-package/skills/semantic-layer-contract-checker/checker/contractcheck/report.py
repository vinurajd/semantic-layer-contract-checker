"""Scorecard renderers: Markdown, standalone HTML, and JSON.

Every rendering carries the same content: the ten cells, each verdict,
and the deciding evidence for every cell. The HTML page is fully
standalone (inline CSS, no external assets).
"""

from __future__ import annotations

import html
import json

from .engine import NOT_ASSESSABLE, NOT_DOCUMENTED, REDUCED, SUPPORTED, Scorecard

FRAMEWORK_CREDIT = (
    "Framework: the machine-consumption contract from \"The Machine-Consumption "
    "Contract of Business Intelligence: A Documentation Audit of Six Semantic "
    "Layers\" by Vinuraj Devaraj."
)
CREATOR_LINE = "Semantic Layer Contract Checker · Created by Vinuraj Devaraj, Independent Researcher"

_BADGE = {
    SUPPORTED: ("supported", "#1a7f37"),
    REDUCED: ("reduced", "#b58900"),
    NOT_DOCUMENTED: ("not documented", "#b42318"),
    NOT_ASSESSABLE: ("not assessable", "#5f6368"),
}


def summary_line(sc: Scorecard) -> str:
    c = sc.counts()
    return (f"{sc.project_name} [{sc.platform}]: "
            f"supported {c[SUPPORTED]} · reduced {c[REDUCED]} · "
            f"not documented {c[NOT_DOCUMENTED]} · "
            f"not assessable {c[NOT_ASSESSABLE]} (of 10 requirements)")


def to_dict(sc: Scorecard) -> dict:
    return {
        "tool": "Semantic Layer Contract Checker",
        "platform": sc.platform,
        "project": sc.project_name,
        "counts": sc.counts(),
        "cells": [
            {
                "requirement": cell.requirement,
                "title": cell.title,
                "family": cell.family,
                "verdict": cell.verdict,
                "evidence": cell.evidence,
                "sub_checks": [
                    {"name": n, "finding": f} for n, f in cell.sub_checks
                ],
            }
            for cell in sc.cells
        ],
        "framework": FRAMEWORK_CREDIT,
        "creator": CREATOR_LINE,
    }


def render_json(sc: Scorecard) -> str:
    return json.dumps(to_dict(sc), indent=2) + "\n"


def render_markdown(sc: Scorecard) -> str:
    c = sc.counts()
    lines = [
        f"# Machine-Consumption Contract Scorecard — {sc.project_name}",
        "",
        f"Platform: **{sc.platform}** · "
        f"Supported: **{c[SUPPORTED]}** · Reduced: **{c[REDUCED]}** · "
        f"Not documented: **{c[NOT_DOCUMENTED]}** · "
        f"Not assessable: **{c[NOT_ASSESSABLE]}**",
        "",
        "| Req | Requirement | Family | Verdict |",
        "|-----|-------------|--------|---------|",
    ]
    for cell in sc.cells:
        lines.append(f"| {cell.requirement} | {cell.title} | {cell.family} "
                     f"| {cell.verdict} |")
    lines += ["", "## Evidence by requirement", ""]
    for cell in sc.cells:
        lines.append(f"### {cell.requirement} — {cell.title}: {cell.verdict}")
        for ev in cell.evidence:
            lines.append(f"- {ev}")
        for name, finding in cell.sub_checks:
            lines.append(f"- Sub-check, {name}: {finding}")
        lines.append("")
    lines += ["---", FRAMEWORK_CREDIT, "", CREATOR_LINE, ""]
    return "\n".join(lines)


def render_html(sc: Scorecard) -> str:
    c = sc.counts()
    rows = []
    for cell in sc.cells:
        label, color = _BADGE[cell.verdict]
        ev_items = "".join(f"<li>{html.escape(e)}</li>" for e in cell.evidence)
        sub_items = "".join(
            f"<li><em>Sub-check, {html.escape(n)}:</em> {html.escape(f)}</li>"
            for n, f in cell.sub_checks)
        rows.append(
            f"<tr><td class='req'>{cell.requirement}</td>"
            f"<td><strong>{html.escape(cell.title)}</strong><br>"
            f"<span class='fam'>{html.escape(cell.family)}</span>"
            f"<ul>{ev_items}{sub_items}</ul></td>"
            f"<td><span class='badge' style='background:{color}'>"
            f"{html.escape(label)}</span></td></tr>")
    summary = (f"Supported: <strong>{c[SUPPORTED]}</strong> · "
               f"Reduced: <strong>{c[REDUCED]}</strong> · "
               f"Not documented: <strong>{c[NOT_DOCUMENTED]}</strong> · "
               f"Not assessable: <strong>{c[NOT_ASSESSABLE]}</strong>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Machine-Consumption Contract Scorecard — {html.escape(sc.project_name)}</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       margin: 2rem auto; max-width: 880px; padding: 0 1rem; color: #1f2328; }}
h1 {{ font-size: 1.5rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #d0d7de; padding: 0.6rem; vertical-align: top;
         text-align: left; }}
th {{ background: #f6f8fa; }}
td.req {{ font-weight: 700; white-space: nowrap; }}
.fam {{ color: #57606a; font-size: 0.85rem; }}
.badge {{ color: #fff; border-radius: 1em; padding: 0.15em 0.7em;
         font-size: 0.85rem; white-space: nowrap; }}
ul {{ margin: 0.4rem 0 0; padding-left: 1.1rem; }}
footer {{ margin-top: 2rem; color: #57606a; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>Machine-Consumption Contract Scorecard — {html.escape(sc.project_name)}</h1>
<p>Platform: <strong>{html.escape(sc.platform)}</strong> · {summary}</p>
<table>
<tr><th>Req</th><th>Requirement and deciding evidence</th><th>Verdict</th></tr>
{''.join(rows)}
</table>
<footer>
<p>{html.escape(FRAMEWORK_CREDIT)}</p>
<p>{html.escape(CREATOR_LINE)}</p>
</footer>
</body>
</html>
"""
