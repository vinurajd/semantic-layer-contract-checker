# Build audit — Semantic Layer Contract Checker v1 (Nov 19, 2026)

Local build only. No git push, no PyPI publish, no external contact was
made or attempted.

## What was built

A Python library and CLI (`contractcheck`, src layout under
`src/contractcheck/`) implementing the design brief
(`semantic-layer-contract-checker-brief-2026-11-19.md`, including the
marketplace addendum's design consequence: a standalone scoring engine
that marketplace wrappers can sit on later).

- `model.py` — normalized intermediate model. Adapters populate
  Artifacts (metrics, measures, models, commands) whose fields are named
  for contract elements, plus SourceArtifacts and ContextEntries
  (reviewed shared context as a first-class artifact type).
- `engine.py` — scoring engine for R1 to R10 with the paper's four-value
  vocabulary (documented as supported; documented with reduction; not
  documented; not assessable) and the paper's rules: conjunctive
  requirements need every element; silence is never coded as support or
  refusal; authoring-surface evidence caps a cell at reduction; every
  cell names its deciding evidence. R7 carries the named "coverage
  statement" sub-check.
- `adapters/dbt.py` — parses a dbt manifest.json: semantic models
  (measures, dimensions, time granularity), metrics (simple, ratio,
  cumulative, derived, conversion), model nodes (lineage, access,
  deprecation_date), sources (loaded_at_field, freshness thresholds).
- `adapters/promptql.py` — parses Hasura DDN metadata YAML (ObjectType,
  Model, Command, Relationship, ModelPermissions, CommandPermissions,
  TypePermissions) plus shared-context documents (BusinessDefinition,
  Assumption, CoverageStatement, or a top-level `context:` list).
  Relationships and object fields map to declared slicing paths;
  permissions map to access evidence; reviewed glossary entries map to
  provenance notes and certification-adjacent evidence. Where DDN
  metadata has no equivalent for a contract element, the field is left
  unset and the engine codes it not documented; nothing is inferred
  from names.
- `report.py` — Markdown, standalone HTML (inline CSS, no external
  assets), and JSON renderers with identical content; `cli.py` —
  `contractcheck check --platform dbt|promptql --input <path>
  --format md|html|json --out <file>`, stdout summary in the paper's
  terms, `--strict` CI exit code.
- `examples/` — one small fixture per platform and the four generated
  scorecards under `examples/output/`.
- `tests/` — pytest suite (see results below). `README.md`, `LICENSE`
  (MIT), `pyproject.toml`.

## Proof runs (real output, regenerated in place)

- dbt fixture (`examples/dbt/manifest.json`, 3 metrics + 3 measures,
  3 models, 2 sources): **supported 2 · reduced 7 · not documented 0 ·
  not assessable 1**. Supported: R1, R3. Not assessable: R8. The
  reduction pattern is the fixture's designed gaps: one measure with no
  time dimension (R2), one source with no freshness thresholds (R4),
  access declared only on an underlying model (R5), owners without any
  certification marker (R6), units and caveats on one metric only (R7),
  deprecation_date on a model but on no metric (R9), name-based
  identity (R10).
- PromptQL fixture (`examples/promptql/metadata/`, 2 models, 1 command,
  3 reviewed context entries): **supported 1 · reduced 5 · not
  documented 3 · not assessable 1**. Supported: R1. Not documented:
  R4 (DDN metadata declares no freshness equivalent), R7 (no units,
  grain, or caveats declared; the coverage statement sub-check is
  separately **declared**, from the fixture's CoverageStatement entry),
  R9 (no deprecation or version field). Reduced: R2 (aggregation and
  slicing paths declared; grain and time behavior not), R3 and R6
  (reviewed shared context, capped as provenance- and
  certification-adjacent evidence), R5 (role permissions declared;
  enforcement not statically assessable), R10 (name-based identity).

README sample counts were checked against these generated outputs and
match exactly.

## Test results

`pytest` 9.2.0 on Python 3.12.3 (project venv): **21 passed, 0 failed**.
Coverage: engine coding rules (conjunctive R2 supported/reduced/not
documented; silence handling on an empty project; R8 always not
assessable with its reason; R5 configuration cap; R9 underlying-model
locus cap; R4 partial freshness; R7 coverage sub-check both ways;
counts sum to 10; reviewed context caps R6 at reduction) and both
adapters parsing their fixtures (inheritance of measure semantics by
metrics, freshness parsing, access and deprecation on model nodes;
DDN dimensions from fields and relationships, permissions as access,
coverage entry parsing, glossary-to-provenance mapping).

## Not assessable, and why (recorded, not hidden)

- **R8, always.** Structured rejection is runtime behavior of the query
  surface; project files cannot evidence it. The cell states this and
  is never silently scored.
- **R5, enforcement half.** Role and access declarations are coded as
  configuration evidence (reduction at best); whether enforcement binds
  the caller's own identity at query time is runtime behavior.
- **R7, payload half.** The checker scores declared units, grain, and
  caveats; whether the response payload itself carries them is runtime
  behavior. The scorecard says so in the cell's evidence.

## Lessons comparison (mandatory pass, per AGENTS.md Nov 18, 2026 rule)

Against AGENTS.md, item by item:

- *Understand before concluding* — checked: the brief and the
  manuscript's R1–R10 definitions (lines 33–47) were read in full
  before any code was written; the engine's vocabulary and rules are
  the manuscript's, not reconstructed from memory.
- *Lessons comparison on every build* — this section is that pass.
- *Text editing* — checked: no `sed` anywhere; all file creation and
  edits used exact-match file tools.
- *Fact verification against the primary source* — checked: requirement
  definitions, the four families, the conjunctive rule, and the
  locus-partition rule were taken from the manuscript text itself.
- *Rendered-output verification* (venue-builds lesson, applied by
  analogy) — checked: both HTML scorecards were parsed and verified as
  complete pages (doctype, closing `</html>`, header + 10 rows, key
  text present in extraction), not merely written.
- *Deliverable hygiene* — checked: README and scorecards contain only
  reader-facing material; no internal file names, IDs, or process
  narration. This audit is a separate working file, not shipped in the
  scorecards.
- *Single-version rule / no version language* — checked: scorecards are
  regenerated in place at fixed paths; no `_v2` or "corrected" copies.
- *No-preprint-reference rule* — checked: the framework is credited by
  paper title only, in the README, the report footer, and the package
  docstring. No DOI and no preprint link anywhere (verified by grep).
- *Repo-first rule* — NOT DONE, deliberately: this task was scoped
  local-only with no push. Recorded here as an open step for the
  brief's Stage 3, which happens on the user's word; not silently
  skipped.
- *Probability reporting / score calibration* — checked by design: the
  tool emits categorical codings only; no percentages, no derived
  products of judgments.
- *Venue gate, scope fitment, India shelf, cross-domain pass, editor
  pitch, signature rules* — not applicable: no venue, outreach, or
  email in this build. No external contact of any kind was made.

Against the standing self-review checklist, the items that transfer to
a code build:

- *Negative claims trace to a documented protocol* — checked by
  design: a "not documented" coding is produced only from the parsed
  artifacts of the project under audit, with the deciding evidence
  printed in the cell; the engine states that silence is not refusal.
- *Headline results flagged at point of use* — checked: the R5, R7,
  and R8 caveats sit inside those cells' evidence, not in a general
  disclaimer.
- *Novelty and claims scoped* — checked: the README states what the
  tool audits and carries an explicit "What the tool does not do"
  section; no platform-certification claim is made.
- *One concept, one settlement, everywhere* — checked: the verdict
  vocabulary is defined once in `engine.py` and imported by the
  report renderers and CLI; the creator line is identical in the
  README, the scorecard footer, and the package docstring.
- *Promises map to deliverables* — checked: every README claim was
  exercised (both platforms, all three formats, `--strict`, the two
  sample scorecards linked and present, counts matching).
- *Counting reconciles* — checked: counts sum to 10 by construction
  and by test.
- *Declaration consistency* — checked: no AI-use or authorship
  statement in the deliverables contradicts another; the creator is
  named once, consistently, as Vinuraj Devaraj, Independent
  Researcher; no employer is named anywhere in the tree (verified by
  grep).
- *Manuscript-only items* (methodology section, figures, reference
  order and census, float citation, abstract findings test, desk and
  acceptance separation) — not applicable to a code build; the
  transferable analogues are covered above.

## Open items (for the parent agent / user's word)

- Repo posting and PyPI publication are the brief's Stage 3 and were
  out of scope here.
- The venv at `.venv/` is a local build convenience and is gitignored.

---

# Wrappers build — GitHub Action and MCP server (Nov 19, 2026)

Local build only, on top of the v1 library and CLI. No git push, no
publish, no marketplace listing, no external contact was made or
attempted. This section is the build record for the two marketplace
wrappers named in the design brief's addendum (routes 1 and 2; the
dbt Hub package and the VS Code extension were not in this task).

## What was built

- **`action.yml`** (repository root; a root-level action.yml is what
  a GitHub Marketplace action listing requires) — a **composite**
  Action. Judgment call, recorded: composite over Docker, because the
  checker is a small pure-Python package; a Docker Action would add
  an image build and a registry surface for no capability gain, and
  the composite steps (setup-python, `pip install` of the Action's
  own checkout via `github.action_path`, then the stock CLI) keep the
  Action on the library's single scoring code path. Inputs mirror the
  CLI surface: `platform`, `input`, `format`, `output`, `strict`,
  `upload-artifact`, `artifact-name`, `comment-on-pr`,
  `python-version`. The summary and artifact steps carry
  `if: always()`, so when `--strict` fails the build the scorecard is
  still published to the job summary (Markdown) and uploaded as an
  artifact before the job goes red. The optional pull request comment
  (from the brief: scorecard as PR comment and job summary) uses the
  `gh` CLI with the workflow token and is off by default.
- **`ACTION.md`** — usage documentation: dbt and PromptQL workflow
  examples, the PR-comment variant with its permission requirement,
  the full input table, and behavior notes.
- **`src/contractcheck/mcp_server.py`** — an MCP server on the
  **official `mcp` Python SDK**, stdio transport. The SDK was not in
  the project venv at the start of this build; it was installed from
  PyPI into the venv (mcp 2.3.0), so the hand-rolled JSON-RPC fallback
  the task allowed for was not needed. Tools: `check_dbt_manifest`
  and `check_promptql_metadata` (path plus `output_format` of json or
  markdown; both return an envelope carrying the summary line and the
  scorecard, rendered by the same `report.py` renderers the CLI
  uses), and `list_requirements` (the ten requirements with titles
  and families read from the engine at call time, the question each
  answers, and the verdict vocabulary). The tool handlers are plain
  functions over the library; `build_server()` registers them
  unchanged, so the tested surface and the served surface are the
  same functions. `main()` runs the server; the console script is
  `contractcheck-mcp`, and `python -m contractcheck.mcp_server` also
  works.
- **`pyproject.toml`** — the SDK is an optional extra,
  `contractcheck[mcp]` (`mcp>=1.0`), so the base library and CLI
  install stays dependency-light (PyYAML only); the
  `contractcheck-mcp` console script is registered.
- **`README.md`** — two short sections added ("In CI: the GitHub
  Action" and "From an AI agent: the MCP server") with the install
  and client-configuration snippets, pointing to ACTION.md for the
  full Action reference.
- **Tests** — `tests/test_mcp_server.py` (11 tests) and
  `tests/test_action_yml.py` (4 tests), below.

## Design decisions a reviewer should know

- **SDK major-version drift, handled in one place.** The installed
  SDK is 2.x, where the server class is `MCPServer`
  (`mcp.server.mcpserver`); in 1.x the same class was `FastMCP`
  (`mcp.server.fastmcp`). `mcp_server.py` imports the 2.x name and
  falls back to the 1.x name, so the extra `mcp>=1.0` resolves under
  either major. Only that import is version-sensitive; everything
  else uses the stable tool-registration surface.
- **Error behavior differs by layer, and both layers are pinned by
  tests.** Handlers raise `FileNotFoundError` / `ValueError` on bad
  input (asserted directly). Over the wire, the SDK's protocol layer
  converts that to an MCP `isError` result with a generic message
  (the SDK deliberately does not leak exception text), asserted by
  the stdio test. The in-process `call_tool` helper in SDK 2.x
  instead propagates the exception; a test pins that too, so a future
  SDK upgrade that changes either behavior fails loudly here rather
  than silently in an agent session.
- **One settlement for the vocabulary, extended.** `list_requirements`
  takes titles and families from the engine's own cells (scoring an
  empty project) rather than restating them; only the per-requirement
  questions are local to the server module, matching the README
  table's wording. A drift between the engine's titles and the
  server's list is therefore impossible by construction, and a test
  asserts R7 and R8 titles against the engine.
- **The Action cannot be executed locally.** GitHub's runners are
  the only place a composite Action runs, and this build is local
  only by instruction. The action.yml is therefore verified
  structurally (parsed YAML; metadata, inputs, step wiring, and the
  `always()` publication guard asserted by tests) and by keeping
  every run step a thin call into surfaces that are executed locally:
  the pip install of this tree and the `contractcheck` CLI. The
  residual risk is runner-side (expression syntax, action version
  availability) and is recorded here rather than smoothed over; the
  first real workflow run after repo posting is the true end-to-end
  check.

## Test results

`pytest` 9.2.0 on Python 3.12.3 (project venv, after reinstalling the
editable package so the new console script registered):
**36 passed, 0 failed** — the 21 v1 tests unchanged, plus 15 new:

- MCP handlers (6): dbt fixture counts match the v1 proof run
  (2 / 7 / 0 / 1) through the tool envelope; Markdown format returns
  the rendered scorecard with the creator line; PromptQL counts match
  (1 / 5 / 3 / 1) and the R7 coverage-statement sub-check is present;
  unknown format raises; missing paths raise on both tools;
  `list_requirements` returns R1 to R10 in order with the engine's
  verdict vocabulary.
- MCP registration and in-process calls (4): the server registers
  exactly the three named tools with descriptions; `call_tool` for
  `list_requirements` and `check_dbt_manifest` returns structured
  content with the proof-run counts; a bad path propagates as pinned
  above.
- MCP stdio protocol (1): a subprocess speaking raw JSON-RPC over
  stdio completes initialize (server name `contractcheck`), lists
  the three tools, calls `list_requirements`, and receives an
  `isError` result for a bad-path `check_dbt_manifest` call. No
  network; the server is a child process of the test.
- GitHub Action (4): Marketplace shape (root composite action.yml,
  name, description, author, branding); inputs cover the CLI surface
  with the required flags and defaults the docs promise; steps
  install from `github.action_path`, run the CLI with `--strict`
  handling, and publish via `GITHUB_STEP_SUMMARY` and
  upload-artifact with the `always()` guard; ACTION.md exists and
  documents both platforms and the creator line.

Also verified outside pytest: the installed `contractcheck-mcp`
console script answered an initialize request over stdio with the
server's instructions and tool capability.

## Lessons comparison (mandatory pass, per AGENTS.md Nov 18, 2026 rule)

Against AGENTS.md, item by item:

- *Understand before concluding* — checked: the brief's marketplace
  addendum and the v1 audit were read in full before building; both
  wrappers wrap the existing engine, adapters, and renderers, as the
  addendum's design consequence prescribes ("thin wrappers over it").
  The one scope question the task left open (composite or Docker)
  was decided on the package's actual shape and is recorded above.
- *Lessons comparison on every build* — this section is that pass.
- *Text editing* — checked: no `sed` anywhere; all file creation and
  edits used exact-match file tools.
- *Fact verification against the primary source* — checked: the SDK's
  API was verified against the installed package itself (imports,
  signatures, a live prototype call, and a live stdio exchange), not
  from memory of the 1.x API; that check is what caught the
  FastMCP-to-MCPServer rename before any server code was written.
  Marketplace's root-action.yml requirement and the composite
  step semantics are the documented GitHub behavior the file was
  shaped to.
- *Rendered-output verification* (applied by analogy) — checked: the
  MCP server was exercised through its real rendered surface (raw
  JSON-RPC over stdio, plus the installed console script), and the
  action.yml through a YAML parse with structural assertions; neither
  wrapper is "verified" from source reading alone.
- *Deliverable hygiene* — checked: README and ACTION.md contain only
  reader-facing material; no internal file names, IDs, or process
  narration. This audit remains a separate working file.
- *Single-version rule / no version language* — checked: wrappers
  were added in place; no `_v2` or "corrected" copies of anything.
  (The `@v1` in usage examples is the consumer-side Action tag
  convention, not a file name.)
- *No-preprint-reference rule* — checked: no DOI or preprint link in
  any new or edited file (verified by grep across action.yml,
  ACTION.md, mcp_server.py, both new test files, and the README
  additions).
- *Repo-first rule* — NOT DONE, deliberately, same as v1: this task
  was scoped local-only with no push. The Action and the MCP listing
  both become real only at the brief's Stage 3, on the user's word;
  recorded here, not silently skipped.
- *Probability reporting / score calibration* — checked: no figures
  of any kind were produced; the wrappers emit the same categorical
  codings as the library.
- *Venue gate, scope fitment, India shelf, cross-domain pass, editor
  pitch, signature rules* — not applicable: no venue, outreach, or
  email in this build. No external contact of any kind was made; the
  single network operation was installing the `mcp` package into the
  local venv from PyPI, which the task's SDK instruction required.

Against the standing self-review checklist, the items that transfer
to a code build:

- *Negative claims trace to a documented protocol* — checked: the
  audit states plainly what could not be executed locally (the
  Action on a real runner) and what stands in for it (structural
  tests plus locally executed surfaces), rather than claiming an
  end-to-end CI verification that did not happen.
- *Headline results flagged at point of use* — checked: the
  error-behavior difference between the wire and the in-process
  helper is flagged in the design decisions above and pinned by
  tests, not buried.
- *Novelty and claims scoped* — checked: README and ACTION.md claim
  only what the wrappers do; the Action's docs state it runs the
  same CLI, and the MCP section names the three tools and nothing
  more. No registry or Marketplace listing is claimed; none exists
  yet.
- *One concept, one settlement, everywhere* — checked: verdict
  vocabulary, requirement titles, families, and the creator line are
  imported from `engine.py` and `report.py` by both wrappers; the
  creator is named identically (Vinuraj Devaraj, Independent
  Researcher) in action.yml, ACTION.md, the README additions, and
  the server module; no employer is named anywhere in the new or
  edited files (verified by grep).
- *Promises map to deliverables* — checked: every documented input
  exists in action.yml with the documented default (asserted by
  test); every documented MCP tool is registered (asserted by test);
  the README's client snippet names the console script that the
  reinstall actually created (verified in the venv).
- *Counting reconciles* — checked: 21 prior tests plus 15 new equals
  the 36 the suite reports; the MCP tool counts asserted in tests
  are the v1 proof-run counts, unchanged.
- *Declaration consistency* — checked: the pyproject extra and the
  README install line agree (`contractcheck[mcp]`); the framework
  credit in MCP output is the same `report.py` constant the CLI
  prints.
- *Manuscript-only items* (methodology section, figures, reference
  order and census, float citation, abstract findings test, desk and
  acceptance separation) — not applicable to a code build; the
  transferable analogues are covered above.

## Open items (wrappers)

- First real workflow run of the Action, and any MCP registry
  listing, belong to the brief's Stage 3 (repo posting and launch),
  on the user's word.
- The `mcp` SDK now lives in the local venv as an installed (not
  vendored) dependency; the venv remains gitignored.
