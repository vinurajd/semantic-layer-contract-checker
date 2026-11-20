# GitHub Action: Semantic Layer Contract Checker

The checker ships as a GitHub Action, so a repository can audit its own
semantic layer in CI: every pull request gets a contract scorecard in
the job summary and as a downloadable artifact, and the build can fail
when a requirement is coded *not documented*.

## Usage

Audit a dbt project from its compiled manifest (build the manifest
first, for example with `dbt compile` or `dbt docs generate`, both of
which write `target/manifest.json`):

```yaml
name: Contract check
on: [pull_request]

jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Build your manifest here, e.g.:
      # - run: pip install dbt-core dbt-duckdb && dbt compile

      - uses: vinurajd/contract-checker@v1
        with:
          platform: dbt
          input: target/manifest.json
          strict: "true"
```

Audit a PromptQL / Hasura DDN metadata directory:

```yaml
      - uses: vinurajd/contract-checker@v1
        with:
          platform: promptql
          input: metadata/
          format: html
```

Post the scorecard as a pull request comment as well (Markdown only;
the job needs `pull-requests: write`):

```yaml
permissions:
  contents: read
  pull-requests: write

      - uses: vinurajd/contract-checker@v1
        with:
          platform: dbt
          input: target/manifest.json
          comment-on-pr: "true"
```

## Inputs

| Input | Required | Default | Purpose |
|-------|----------|---------|---------|
| `platform` | yes | | `dbt` or `promptql` |
| `input` | yes | | dbt: manifest.json file or project directory. PromptQL: metadata directory |
| `format` | no | `md` | Scorecard format: `md`, `html`, or `json` |
| `output` | no | `contract-scorecard.md` | Scorecard file to write |
| `strict` | no | `"false"` | `"true"` fails the build when any requirement is coded *not documented* |
| `upload-artifact` | no | `"true"` | Upload the scorecard as a workflow artifact |
| `artifact-name` | no | `contract-scorecard` | Name of the uploaded artifact |
| `comment-on-pr` | no | `"false"` | Post the scorecard as a pull request comment (Markdown only) |
| `python-version` | no | `3.12` | Python version used to run the checker |

## Behavior notes

- The scorecard is written to the job summary (Markdown format) and
  uploaded as an artifact even when `--strict` fails the build, so a
  red build still shows exactly which requirements are not documented
  and the evidence behind each coding.
- The Action is a composite Action: it installs the checker from the
  Action's own checkout with pip and runs the same `contractcheck`
  CLI documented in the README. There is no separate scoring code path
  to drift from the library.
- Verdicts use the audit's four-value vocabulary: *documented as
  supported*, *documented with reduction*, *not documented*, *not
  assessable*. Runtime behavior that project files cannot evidence
  (R8, and the enforcement half of R5) is reported as not assessable,
  never silently scored.

Created by Vinuraj Devaraj, Independent Researcher.
