"""Model Context Protocol (MCP) server wrapper.

Exposes the contract checker to AI agents over MCP (stdio transport),
so an agent can audit the semantic layer it is about to consume and
read the scorecard itself: the machine consumer checking the
machine-consumption contract.

Tools:
  check_dbt_manifest(path, output_format="json")
  check_promptql_metadata(path, output_format="json")
  list_requirements()

Built on the official MCP Python SDK (MCPServer in SDK 2.x, FastMCP in
SDK 1.x; the import below accepts either). Install with:

  pip install "contractcheck[mcp]"

Run with:

  contractcheck-mcp            (stdio transport)

Created by Vinuraj Devaraj, Independent Researcher.
"""

from __future__ import annotations

from typing import Any

from . import __version__, engine, report
from .adapters import dbt as dbt_adapter
from .adapters import promptql as promptql_adapter
from .model import Project

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # SDK 1.x used the FastMCP name for the same class.
    from mcp.server.fastmcp import FastMCP as MCPServer

SERVER_NAME = "contractcheck"

# The question each requirement lets a machine consumer answer (the
# same wording as the README's requirements table). Titles and families
# are not repeated here; list_requirements reads them from the engine,
# so the vocabulary has one settlement.
QUESTIONS = {
    "R1": "Can I discover every governed definition through a "
          "programmatic surface?",
    "R2": "Are aggregation, grain, slicing dimensions, and time "
          "behavior declared for mechanical checking?",
    "R3": "Can I read where this definition came from and what it "
          "derives from?",
    "R4": "Can I state how current the underlying data is, from the "
          "surface I consume?",
    "R5": "Are access rules declared, and enforced against my own "
          "machine identity at query time?",
    "R6": "Can I tell, in machine-readable form, that the organization "
          "vouches for this artifact?",
    "R7": "Do results carry their units, grain, and caveats, and state "
          "the population they represent?",
    "R8": "Does an invalid request receive an error I can act on, "
          "rather than a silent empty result?",
    "R9": "Can I poll for version and deprecation signals instead of "
          "discovering breakage after the fact?",
    "R10": "Does a metric carry an identity that survives renaming?",
}


# ------------------------------------------------------------- handlers
# Plain functions over the library. The MCP registration below is a
# thin wrapper; these handlers are the unit-tested surface.

def _run_check(adapter, path: str, output_format: str) -> dict[str, Any]:
    fmt = (output_format or "json").lower()
    if fmt not in ("json", "markdown"):
        raise ValueError("output_format must be 'json' or 'markdown'")
    project = adapter.load_project(path)
    scorecard = engine.score_project(project)
    if fmt == "markdown":
        return {"format": "markdown",
                "summary": report.summary_line(scorecard),
                "markdown": report.render_markdown(scorecard)}
    return {"format": "json",
            "summary": report.summary_line(scorecard),
            "scorecard": report.to_dict(scorecard)}


def check_dbt_manifest(path: str,
                       output_format: str = "json") -> dict[str, Any]:
    """Audit a dbt project against the machine-consumption contract.

    path: the project's manifest.json file, or the project directory
    containing it. output_format: "json" for the structured scorecard
    (default) or "markdown" for the rendered scorecard. The scorecard
    codes each of the ten requirements as documented as supported,
    documented with reduction, not documented, or not assessable, with
    the deciding evidence for every cell.
    """
    return _run_check(dbt_adapter, path, output_format)


def check_promptql_metadata(path: str,
                            output_format: str = "json") -> dict[str, Any]:
    """Audit PromptQL / Hasura DDN metadata against the contract.

    path: the metadata directory (ObjectType, Model, Command,
    Relationship, and permission YAML, plus any shared-context
    documents; reviewed context entries are read as first-class
    artifacts). output_format: "json" (default) or "markdown". The
    scorecard uses the same four-value vocabulary and names the
    deciding evidence for every cell.
    """
    return _run_check(promptql_adapter, path, output_format)


def list_requirements() -> dict[str, Any]:
    """List the ten requirements of the machine-consumption contract.

    Returns each requirement's identifier, title, family, and the
    question it lets a machine consumer answer, plus the four-value
    verdict vocabulary the scorecards use.
    """
    cells = engine.score_project(Project(platform="", name="")).cells
    return {
        "requirements": [
            {"requirement": c.requirement, "title": c.title,
             "family": c.family, "question": QUESTIONS[c.requirement]}
            for c in cells
        ],
        "verdicts": list(engine.VERDICTS),
        "framework": report.FRAMEWORK_CREDIT,
        "creator": report.CREATOR_LINE,
    }


# --------------------------------------------------------------- server

def build_server() -> MCPServer:
    server = MCPServer(
        SERVER_NAME,
        version=__version__,
        instructions=(
            "Audit a semantic-layer project (a dbt manifest or "
            "PromptQL / Hasura DDN metadata) against the ten-requirement "
            "machine-consumption contract before consuming it. Use "
            "list_requirements to read the contract, then "
            "check_dbt_manifest or check_promptql_metadata to score a "
            "project; every scorecard cell names its deciding evidence."
        ),
    )
    server.tool()(check_dbt_manifest)
    server.tool()(check_promptql_metadata)
    server.tool()(list_requirements)
    return server


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
