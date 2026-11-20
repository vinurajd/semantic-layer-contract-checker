# Semantic Layer Contract Checker — Frequently Asked Questions

## Getting started

**What does this skill do?**
It audits a semantic-layer project against the ten-requirement machine-consumption contract: the declarations an AI consumer needs in order to discover metrics, understand them, trust them, and use their results safely. It produces a scorecard coding each requirement as supported, documented with reduction, not documented, or not assessable, with the deciding evidence named for every cell.

**Which platforms does it check?**
Two today: dbt (from the project's compiled manifest) and PromptQL / Hasura DDN (from the metadata directory). Other semantic layers need an adapter that does not exist yet, and the skill says so rather than approximating a score.

**What do I need to give it?**
For dbt, the `manifest.json` your project already compiles to (usually under `target/`). For PromptQL, the metadata directory of the DDN project. Nothing else: no warehouse connection, no credentials.

**What does it need installed?**
Python 3.10 or later and PyYAML. The checker itself is bundled inside the skill; there is nothing else to install.

## The scorecard

**What do the four codings mean?**
Supported: the project declares the requirement in machine-checkable form. Documented with reduction: something is declared, but an element is missing or the evidence lives only where authors work, not where machines consume. Not documented: the project files declare nothing that answers the requirement. Not assessable: the requirement is about runtime behaviour that project files cannot evidence.

**Why is R8 always "not assessable"?**
Structured rejection is what a server does at query time when a request is invalid. Project files cannot show that behaviour, so the checker reports it honestly as not assessable instead of guessing. The same applies to the enforcement half of R5: declared access rules can be checked in files; enforcement against a live identity cannot.

**What is the coverage statement?**
A named sub-check inside R7, the result contract. It asks whether the project declares that answers state the population they represent, so a figure computed over the rows a user is permitted to see is not described as company-wide. In the bundled examples it reads declared on the PromptQL fixture and not documented on the dbt fixture.

**My score has "not documented" cells. Is my semantic layer bad?**
Not necessarily unusual, and that is the point of the check. The trust half of the contract (freshness, certification, result terms, deprecation, stable identity) is what project files most often leave undeclared, across every platform the underlying audit studied. Each cell names what the checker looked for, which is the list of declarations to add.

**How do I improve a weak cell?**
Add the declaration the scorecard names for that requirement, in the surface a machine consumes, then re-run the checker. The scorecard's evidence lines are written to double as a work list.

## Privacy and limits

**Does my project leave my machine?**
No. The checker reads local files and writes a local scorecard. Nothing is uploaded, and no account or API key is involved.

**Does it connect to my warehouse or semantic layer at runtime?**
No. It audits the declarations in project files. Runtime behaviour, including actual access enforcement and error responses, is outside what files can evidence, and the scorecard marks those requirements not assessable rather than scoring them.

**Where does the framework come from?**
From a documentation audit of six production semantic layers (dbt, Cube, Looker, Snowflake, Microsoft, and AtScale) against ten requirements for machine consumption, with a blind re-coding of the full matrix. This skill applies the same contract to a team's own project files.

**Can it run in CI?**
The skill runs the checker locally. The checker project also ships a GitHub Action wrapper that publishes the scorecard to the job summary and can fail a build on a not documented coding, and an MCP server exposing the same checks to MCP clients.
