"""Structural tests for the GitHub Action wrapper.

The Action itself runs on GitHub's runners, which the test suite
cannot reach; these tests pin the contract the workflow depends on:
a composite action.yml at the repository root (the Marketplace
requirement) that installs this package and runs the same CLI, with
the strict flag, artifact upload, and job summary wired in.
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = yaml.safe_load((ROOT / "action.yml").read_text(encoding="utf-8"))


def test_action_metadata_and_marketplace_shape():
    assert ACTION["name"] == "Semantic Layer Contract Checker"
    assert "machine-consumption contract" in ACTION["description"]
    assert ACTION["author"] == "Vinuraj Devaraj"
    # A Marketplace action listing requires action.yml at the root and
    # a composite (or Docker) runner declared in it.
    assert ACTION["runs"]["using"] == "composite"
    assert ACTION["branding"]["icon"]
    assert ACTION["branding"]["color"]


def test_action_inputs_cover_the_cli_surface():
    inputs = ACTION["inputs"]
    for name in ("platform", "input", "format", "output", "strict",
                 "upload-artifact", "artifact-name", "comment-on-pr",
                 "python-version"):
        assert name in inputs, name
    assert inputs["platform"]["required"] is True
    assert inputs["input"]["required"] is True
    assert inputs["format"]["default"] == "md"
    assert inputs["strict"]["default"] == "false"
    assert inputs["upload-artifact"]["default"] == "true"


def test_action_steps_run_the_checker_and_publish_the_scorecard():
    steps = ACTION["runs"]["steps"]
    run_blocks = "\n".join(s.get("run", "") for s in steps)
    uses = [s.get("uses", "") for s in steps]
    # Installs the package from the Action's own checkout, then runs
    # the same CLI as the library ships: no second scoring code path.
    assert "github.action_path" in run_blocks
    assert "contractcheck" in run_blocks
    assert "--strict" in run_blocks
    assert any(u.startswith("actions/setup-python@") for u in uses)
    # Scorecard leaves the job as an artifact and, for Markdown, in
    # the job summary; both publish even when --strict fails the run.
    assert any(u.startswith("actions/upload-artifact@") for u in uses)
    assert "GITHUB_STEP_SUMMARY" in run_blocks
    upload = next(s for s in steps
                  if s.get("uses", "").startswith("actions/upload-artifact@"))
    assert "always()" in upload["if"]


def test_action_docs_exist_and_match():
    doc = (ROOT / "ACTION.md").read_text(encoding="utf-8")
    assert "platform: dbt" in doc
    assert "platform: promptql" in doc
    assert "strict" in doc
    assert "Vinuraj Devaraj, Independent Researcher" in doc
