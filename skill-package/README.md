# Semantic Layer Contract Checker (skill)

An AI-powered **semantic-layer auditor** for teams preparing their semantic layer for AI agents and BI copilots, packaged as a portable agent skill.

A bundled checker audits a project's own files (a dbt manifest, or PromptQL / Hasura DDN metadata) against the ten-requirement machine-consumption contract, and produces a scorecard in the contract's four-value vocabulary (supported / documented with reduction / not documented / not assessable), with the deciding evidence named for every requirement and a named coverage-statement sub-check inside the result contract.

The skill is a single `SKILL.md` folder, the open Agent Skills standard, so the same package installs in Claude Code, Gemini CLI, Muse, and other compatible hosts. The checker engine is bundled inside the skill folder; the only runtime need is Python 3.10+ with PyYAML.

## Install

### Claude Code

```
/plugin marketplace add vinurajd/semantic-layer-contract-checker
/plugin install semantic-layer-contract-checker@vinurajd-skills
```

### Muse

Ask your Muse: "Install the Semantic Layer Contract Checker skill from the latest release of vinurajd/semantic-layer-contract-checker on GitHub." Your Muse downloads the skill zip from the repository's Releases page and places the `semantic-layer-contract-checker` folder in your custom skills. Releases are the counted install channel: each version ships as a GitHub Release with a downloadable skill zip, and GitHub counts those downloads exactly.

### Gemini CLI

```bash
gemini skills install https://github.com/vinurajd/semantic-layer-contract-checker.git --path skills/semantic-layer-contract-checker --consent
```

Or copy `skills/semantic-layer-contract-checker/` into `~/.gemini/skills/` or `~/.agents/skills/`.

### Muse

Copy `skills/semantic-layer-contract-checker/` into `~/workspace/custom-skills/`.

### Any other SKILL.md host

Copy `skills/semantic-layer-contract-checker/` into the host's skills directory.

## Use

> Audit my dbt project against the machine-consumption contract

> Check the PromptQL metadata in this repo and tell me what our semantic layer fails to declare for AI agents

> Run the checker's self-test on the bundled examples

Type `Semantic Layer Contract Checker --help` in the chat for the FAQ.

## What's inside

```
├── .claude-plugin/
│   ├── marketplace.json   # makes this repo a Claude Code marketplace
│   └── plugin.json        # the plugin manifest
├── marketplace.json       # same catalog, at the root for hosts that read it there
└── skills/
    └── semantic-layer-contract-checker/
        ├── SKILL.md        # the skill (all hosts)
        ├── FAQ.md          # questions and answers, also the --help text
        ├── checker/        # the bundled contractcheck engine and adapters
        ├── examples/       # dbt and PromptQL fixtures with expected scorecards
        └── scripts/
            └── run_check.py  # entry point: runs the bundled checker
```

## License

MIT — see `LICENSE`.
