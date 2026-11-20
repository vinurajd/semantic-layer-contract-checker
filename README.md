# Semantic Layer Contract Checker

When an AI agent queries a semantic layer, the layer's declarations decide
what the agent can know: which metrics exist, what they mean, whether the
numbers are fresh, who certified them, and what the results carry. This tool
audits a semantic-layer **project** against the ten-requirement
machine-consumption contract and prints a scorecard in the audit's own
terms — *documented as supported*, *documented with reduction*,
*not documented*, or *not assessable* — with the deciding evidence named
for every cell.

The paper behind the framework audited vendor documentation. This tool
audits your own project files: the trust half of the contract (freshness,
certification, result terms, identity, deprecation) is exactly what a
team's own definitions usually leave undeclared, and the checker shows
you where.

## The ten requirements

| Req | Requirement | The question a machine consumer must be able to answer |
|-----|-------------|--------------------------------------------------------|
| R1 | Enumerability of definitions | Can I discover every governed definition through a programmatic surface? |
| R2 | Declared semantics | Are aggregation, grain, slicing dimensions, and time behavior declared for mechanical checking? |
| R3 | Provenance and lineage | Can I read where this definition came from and what it derives from? |
| R4 | Freshness signals | Can I state how current the underlying data is, from the surface I consume? |
| R5 | Query-time access control | Are access rules declared, and enforced against my own machine identity at query time? |
| R6 | Certification | Can I tell, in machine-readable form, that the organization vouches for this artifact? |
| R7 | Result contract | Do results carry their units, grain, and caveats — and state the population they represent? |
| R8 | Structured rejection | Does an invalid request receive an error I can act on, rather than a silent empty result? |
| R9 | Deprecation and versioning signals | Can I poll for version and deprecation signals instead of discovering breakage after the fact? |
| R10 | Stable identity | Does a metric carry an identity that survives renaming? |

Coding rules mirror the audit: conjunctive requirements (R2, R7) need
every element for a supported coding; silence is never coded as support
or as refusal; evidence that lives only on an authoring surface caps a
cell at *documented with reduction*; and runtime behavior that project
files cannot evidence (R8, and the enforcement half of R5) is reported
honestly as not assessable rather than silently scored. R7 carries a
named sub-check, the **coverage statement**: whether the project declares
that answers state the population they represent.

## Install

```bash
pip install contractcheck
```

(For this source tree: `pip install -e .`)

## First run

Score a dbt project from its compiled manifest:

```bash
contractcheck check --platform dbt --input path/to/manifest.json \
    --format md --out scorecard.md
```

Score a PromptQL / Hasura DDN metadata directory (reviewed shared-context
entries — business definitions, assumptions, and coverage statements —
are read as first-class artifacts):

```bash
contractcheck check --platform promptql --input path/to/metadata/ \
    --format html --out scorecard.html
```

Formats: `md`, `html` (a clean standalone page), `json`. Add `--strict`
to exit non-zero when any requirement is coded *not documented*, for CI.

## Sample scorecards

Two worked examples ship with the repository, generated from the small
fixtures under `examples/`:

- dbt (sample manifest, 3 metrics and 3 measures):
  [scorecard (Markdown)](examples/output/dbt-scorecard.md) ·
  [scorecard (HTML)](examples/output/dbt-scorecard.html) —
  supported 2 · reduced 7 · not documented 0 · not assessable 1
- PromptQL / Hasura DDN (sample metadata with reviewed shared context):
  [scorecard (Markdown)](examples/output/promptql-scorecard.md) ·
  [scorecard (HTML)](examples/output/promptql-scorecard.html) —
  supported 1 · reduced 5 · not documented 3 · not assessable 1

## In CI: the GitHub Action

This repository is also a GitHub Action. It runs the same CLI against
your own repository in CI, publishes the scorecard to the job summary
and as a build artifact, and can fail the build when a requirement is
coded *not documented*:

```yaml
- uses: vinurajd/contract-checker@v1
  with:
    platform: dbt
    input: target/manifest.json
    strict: "true"
```

Full inputs, a PromptQL example, and the pull request comment option:
[ACTION.md](ACTION.md).

## From an AI agent: the MCP server

The checker also ships as a Model Context Protocol (MCP) server, so
an AI agent can audit the semantic layer it is about to consume and
read the scorecard itself. Install the extra:

```bash
pip install "contractcheck[mcp]"
```

and register the server with your MCP client:

```json
{
  "mcpServers": {
    "contractcheck": { "command": "contractcheck-mcp" }
  }
}
```

Tools: `check_dbt_manifest` and `check_promptql_metadata` return the
scorecard as JSON or Markdown; `list_requirements` returns the ten
requirements and the verdict vocabulary.

## What the tool does not do

It audits project declarations against the contract. It does not certify
platforms, does not test runtime behavior, and does not reproduce the
paper's vendor audit.

## Framework

The contract framework is from "The Machine-Consumption Contract of
Business Intelligence: A Documentation Audit of Six Semantic Layers"
by Vinuraj Devaraj.

Created by Vinuraj Devaraj, Independent Researcher.

## Licence

MIT — see [LICENSE](LICENSE).
