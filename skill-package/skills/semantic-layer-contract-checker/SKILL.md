---
name: semantic-layer-contract-checker
description: Audit a semantic-layer project (a dbt manifest, or PromptQL / Hasura DDN metadata) against the ten-requirement machine-consumption contract for AI consumers, and produce a scorecard in the contract's four-value vocabulary with the deciding evidence named for every requirement. Use when a user wants to check, audit, score, or improve how machine-consumable their semantic layer is, prepare a semantic layer for AI agents or BI copilots, or asks what their semantic layer fails to declare.
---

# Semantic Layer Contract Checker

When an AI agent queries a semantic layer, the layer's declarations decide what the agent can know: which metrics exist, what they mean, whether the numbers are fresh, who certified them, and what the results carry. This skill runs a bundled checker that audits a team's own semantic-layer project files against the ten-requirement machine-consumption contract and produces a scorecard in the contract's own terms, with the deciding evidence named for every cell.

The framework comes from a documentation audit of six production semantic layers. The paper audited what vendors declare; this checker applies the same contract to a project a team owns, which is where the trust half of the contract (freshness, certification, result terms, identity, deprecation) is usually left undeclared.

## Help

If the user's message is `Semantic Layer Contract Checker --help`, or they otherwise ask how to use this skill, what it can do, or for usage help, do not start a check. Open `FAQ.md` in this skill folder and present it: show the file if the host can display files, otherwise answer from it in full. Then offer to run a check.

## The ten requirements

| Req | Requirement | The question a machine consumer must be able to answer |
|-----|-------------|--------------------------------------------------------|
| R1 | Enumerability of definitions | Can I discover every governed definition through a programmatic surface? |
| R2 | Declared semantics | Are aggregation, grain, slicing dimensions, and time behaviour declared for mechanical checking? |
| R3 | Provenance and lineage | Can I read where this definition came from and what it derives from? |
| R4 | Freshness signals | Can I state how current the underlying data is, from the surface I consume? |
| R5 | Query-time access control | Are access rules declared, and enforced against my own machine identity at query time? |
| R6 | Certification | Can I tell, in machine-readable form, that the organisation vouches for this artifact? |
| R7 | Result contract | Do results carry their units, grain, and caveats, and state the population they represent? |
| R8 | Structured rejection | Does an invalid request receive an error I can act on, rather than a silent empty result? |
| R9 | Deprecation and versioning signals | Can I poll for version and deprecation signals instead of discovering breakage after the fact? |
| R10 | Stable identity | Does a metric carry an identity that survives renaming? |

R7 carries a named sub-check, the **coverage statement**: whether the project declares that answers state the population they represent (for example, that a figure computed over permitted rows is not described as company-wide).

## The four codings

Every requirement is coded in exactly one of four values:

- **supported** — the project declares it, in a form a machine can check.
- **documented with reduction** — something is declared, but with a gap: an element missing from a conjunctive requirement, or evidence that lives only on an authoring surface.
- **not documented** — the project files declare nothing that answers the requirement.
- **not assessable** — the requirement concerns runtime behaviour that project files cannot evidence. R8 always lands here, as does the enforcement half of R5. Not assessable is an honest limit, never a pass and never a failure.

Coding rules the checker follows, and the summary must respect: conjunctive requirements (R2, R7) need every element for a supported coding; silence is never coded as support or as refusal; evidence that lives only on an authoring surface caps a cell at documented with reduction.

## Running the checker

The engine is bundled in this skill folder under `checker/` and needs Python 3.10 or later plus PyYAML. If the run fails on a missing `yaml` module, install it (`pip install pyyaml`) and run again. Run through the bundled entry point:

```bash
# dbt: the input is the project's compiled manifest
python3 scripts/run_check.py check --platform dbt --input path/to/manifest.json --format md --out scorecard.md

# PromptQL / Hasura DDN: the input is the metadata directory
python3 scripts/run_check.py check --platform promptql --input path/to/metadata/ --format md --out scorecard.md
```

Formats: `md` (default choice), `html` (a clean standalone page for sharing), `json` (for further processing). Add `--strict` when the user wants a CI-style gate: the run exits non-zero when any requirement is coded not documented. PromptQL metadata is read with reviewed shared-context entries (business definitions, assumptions, coverage statements) as first-class artifacts.

## Workflow

1. **Identify the input.** From the user's project: a dbt manifest (`target/manifest.json` in a dbt project) or a PromptQL / Hasura DDN metadata directory. If the user has neither ready, offer the bundled examples (below) as a demonstration.
2. **Run the checker** in Markdown unless the user asks for HTML or JSON. Deliver the scorecard as a file.
3. **Summarise faithfully.** State the counts per coding; name every **not documented** requirement and the declaration that would answer it; report the R7 coverage-statement sub-check result explicitly; name the **not assessable** cells with their reason. Never soften a coding in the summary, and never present a not documented cell as "probably fine in practice".
4. **Improve, if asked.** Work cell by cell from the evidence the scorecard names: each weak cell states what it looked for and did not find. After the user changes the project, re-run the checker and report the movement.

## Self-test

Two fixtures ship under `examples/`, with their expected scorecards in `examples/output/`. Running the checker on them must reproduce these counts:

- dbt (`examples/dbt/manifest.json`): supported 2, documented with reduction 7, not documented 0, not assessable 1.
- PromptQL (`examples/promptql/metadata/`): supported 1, documented with reduction 5, not documented 3, not assessable 1; the R7 coverage statement reads **declared** on this fixture and **not documented** on the dbt fixture.

## Boundaries

- The checker reads local project files only. Nothing is uploaded or sent anywhere.
- It audits declarations in project files, not runtime behaviour: it does not connect to a warehouse, a dbt server, or a PromptQL project.
- Two adapters ship today: dbt and PromptQL / Hasura DDN. Other semantic layers are out of scope until an adapter exists; say so plainly rather than approximating a score.
