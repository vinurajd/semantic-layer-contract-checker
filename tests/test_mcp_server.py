"""Unit tests for the MCP server wrapper's tool handlers.

Handler level only, plus one protocol-level smoke test that speaks
JSON-RPC to the server over stdio. No network anywhere.
"""

import asyncio
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from contractcheck import engine, mcp_server

ROOT = Path(__file__).resolve().parents[1]
DBT_FIXTURE = ROOT / "examples" / "dbt" / "manifest.json"
PROMPTQL_FIXTURE = ROOT / "examples" / "promptql" / "metadata"


# ------------------------------------------------------------ handlers

def test_check_dbt_manifest_json_counts_match_proof_run():
    result = mcp_server.check_dbt_manifest(str(DBT_FIXTURE))
    assert result["format"] == "json"
    counts = result["scorecard"]["counts"]
    assert counts[engine.SUPPORTED] == 2
    assert counts[engine.REDUCED] == 7
    assert counts[engine.NOT_DOCUMENTED] == 0
    assert counts[engine.NOT_ASSESSABLE] == 1
    assert len(result["scorecard"]["cells"]) == 10


def test_check_dbt_manifest_markdown():
    result = mcp_server.check_dbt_manifest(str(DBT_FIXTURE),
                                           output_format="markdown")
    assert result["format"] == "markdown"
    assert result["markdown"].startswith(
        "# Machine-Consumption Contract Scorecard")
    assert "R10" in result["markdown"]
    assert "Vinuraj Devaraj, Independent Researcher" in result["markdown"]


def test_check_promptql_metadata_json_counts_and_coverage_subcheck():
    result = mcp_server.check_promptql_metadata(str(PROMPTQL_FIXTURE))
    counts = result["scorecard"]["counts"]
    assert counts[engine.SUPPORTED] == 1
    assert counts[engine.REDUCED] == 5
    assert counts[engine.NOT_DOCUMENTED] == 3
    assert counts[engine.NOT_ASSESSABLE] == 1
    r7 = next(c for c in result["scorecard"]["cells"]
              if c["requirement"] == "R7")
    sub_names = [s["name"] for s in r7["sub_checks"]]
    assert "coverage statement" in sub_names


def test_check_rejects_unknown_format():
    with pytest.raises(ValueError):
        mcp_server.check_dbt_manifest(str(DBT_FIXTURE),
                                      output_format="pdf")


def test_check_missing_path_raises():
    with pytest.raises((FileNotFoundError, ValueError)):
        mcp_server.check_dbt_manifest(str(ROOT / "examples" / "nope.json"))
    with pytest.raises((FileNotFoundError, ValueError)):
        mcp_server.check_promptql_metadata(str(ROOT / "examples" / "nope"))


def test_list_requirements_matches_engine_vocabulary():
    result = mcp_server.list_requirements()
    reqs = result["requirements"]
    assert [r["requirement"] for r in reqs] == \
        [f"R{i}" for i in range(1, 11)]
    by_id = {r["requirement"]: r for r in reqs}
    assert by_id["R7"]["title"] == "Result contract"
    assert by_id["R8"]["title"] == "Structured rejection"
    assert all(r["family"] and r["question"] for r in reqs)
    assert result["verdicts"] == list(engine.VERDICTS)


# --------------------------------------------------------- registration

def test_server_registers_the_three_tools():
    server = mcp_server.build_server()
    tools = asyncio.run(server.list_tools())
    assert sorted(t.name for t in tools) == [
        "check_dbt_manifest", "check_promptql_metadata",
        "list_requirements",
    ]
    assert all(t.description for t in tools)


def test_server_call_tool_list_requirements():
    server = mcp_server.build_server()
    result = asyncio.run(server.call_tool("list_requirements", {}))
    assert not result.is_error
    payload = result.structured_content
    assert len(payload["requirements"]) == 10


def test_server_call_tool_check_dbt_manifest():
    server = mcp_server.build_server()
    result = asyncio.run(server.call_tool(
        "check_dbt_manifest", {"path": str(DBT_FIXTURE)}))
    assert not result.is_error
    counts = result.structured_content["scorecard"]["counts"]
    assert counts[engine.SUPPORTED] == 2


def test_server_call_tool_bad_path_raises_in_process():
    # The SDK 2.x in-process call_tool helper propagates a tool's
    # unexpected exception instead of returning an is_error result;
    # the protocol layer converts it to isError on the wire, which
    # the stdio test below pins. Either way the server does not crash.
    server = mcp_server.build_server()
    with pytest.raises(Exception) as excinfo:
        asyncio.run(server.call_tool(
            "check_dbt_manifest", {"path": "/nonexistent/manifest.json"}))
    assert "check_dbt_manifest" in str(excinfo.value)


# ------------------------------------------------------ stdio protocol

def _read_responses(proc, wanted_ids, timeout=30):
    """Collect JSON-RPC responses for wanted_ids from the server's
    stdout, line by line, until all arrive or the deadline passes."""
    lines: queue.Queue = queue.Queue()

    def pump():
        for line in proc.stdout:
            lines.put(line)

    threading.Thread(target=pump, daemon=True).start()
    found = {}
    import time
    deadline = time.monotonic() + timeout
    while len(found) < len(wanted_ids) and time.monotonic() < deadline:
        try:
            line = lines.get(timeout=max(0.1, deadline - time.monotonic()))
        except queue.Empty:
            break
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") in wanted_ids:
            found[msg["id"]] = msg
    return found


def test_stdio_protocol_end_to_end():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.Popen(
        [sys.executable, "-m", "contractcheck.mcp_server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=env, cwd=str(ROOT))
    try:
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "contractcheck-tests",
                                       "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list",
             "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "list_requirements", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "check_dbt_manifest",
                        "arguments": {"path": "/nonexistent.json"}}},
        ]
        for req in requests:
            proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        responses = _read_responses(proc, {1, 2, 3, 4})
    finally:
        proc.kill()
        proc.wait(timeout=10)

    assert set(responses) == {1, 2, 3, 4}, \
        f"missing responses: {sorted(responses)}"
    init = responses[1]["result"]
    assert init["serverInfo"]["name"] == mcp_server.SERVER_NAME
    tools = responses[2]["result"]["tools"]
    assert sorted(t["name"] for t in tools) == [
        "check_dbt_manifest", "check_promptql_metadata",
        "list_requirements",
    ]
    call = responses[3]["result"]
    assert not call.get("isError")
    text = "".join(c.get("text", "") for c in call["content"]
                     if c.get("type") == "text")
    assert "R10" in text and "Stable identity" in text
    # A bad path on the wire is an isError result, not a dead server.
    bad = responses[4]["result"]
    assert bad.get("isError") is True
