# Machine-Consumption Contract Scorecard — northwind_analytics

Platform: **dbt** · Supported: **2** · Reduced: **7** · Not documented: **0** · Not assessable: **1**

| Req | Requirement | Family | Verdict |
|-----|-------------|--------|---------|
| R1 | Enumerability of definitions | Definitions and declared semantics | documented as supported |
| R2 | Declared semantics | Definitions and declared semantics | documented with reduction |
| R3 | Provenance and lineage | Trust signals | documented as supported |
| R4 | Freshness signals | Trust signals | documented with reduction |
| R5 | Query-time access control | Enforcement and the exchange itself | documented with reduction |
| R6 | Certification | Trust signals | documented with reduction |
| R7 | Result contract | Enforcement and the exchange itself | documented with reduction |
| R8 | Structured rejection | Enforcement and the exchange itself | not assessable |
| R9 | Deprecation and versioning signals | Identity and lifecycle | documented with reduction |
| R10 | Stable identity | Identity and lifecycle | documented with reduction |

## Evidence by requirement

### R1 — Enumerability of definitions: documented as supported
- 6 queryable artifacts enumerated from the project's machine-readable surface (3 measure, 3 metric); discovery is a query, not a search through documents.

### R2 — Declared semantics: documented with reduction
- 5/6 queryable artifacts declare all four elements (aggregation, grain, dimensions, time behavior).
- discount_total: missing grain, time behavior.

### R3 — Provenance and lineage: documented as supported
- 6/6 queryable artifacts carry machine-readable lineage to upstream artifacts.
- 2 upstream source(s) declared in the project.
- Underlying models with lineage: 3/3.

### R4 — Freshness signals: documented with reduction
- 1/2 source(s) declare both a loaded-at field and freshness thresholds.

### R5 — Query-time access control: documented with reduction
- 0/6 queryable artifacts carry an access declaration.
- 1 underlying model(s) carry access declarations (authoring surface).
- Configuration evidence only: enforcement at query time against the caller's own machine identity is runtime behavior and is not assessable from project files, so this cell cannot be coded supported by a static audit.

### R6 — Certification: documented with reduction
- 2/6 queryable artifacts declare an owner.
- 0/6 carry a machine-readable certification or endorsement marker.

### R7 — Result contract: documented with reduction
- Units declared: 1/6 artifacts. Grain declared: 5/6. Caveats or usage notes declared: 1/6.
- Scored on project declarations; whether the response payload itself carries units, grain, and caveats is runtime behavior and is not assessable from project files.
- Sub-check, coverage statement: not documented: no declaration found that answers state the population they represent.

### R8 — Structured rejection: not assessable
- Structured rejection is runtime behavior of the query surface: whether an invalid request receives an error an agent can act on cannot be evidenced by project files. Per the audit's honesty rule, this cell is reported as not assessable and is never silently scored; silence is not coded as refusal or as support.

### R9 — Deprecation and versioning signals: documented with reduction
- 0/6 queryable artifacts carry a deprecation signal; 0/6 carry a version field.
- 1 underlying model(s) carry a deprecation signal, one level below the artifacts a consumer queries; that locus caps this cell at reduction.

### R10 — Stable identity: documented with reduction
- 0/6 queryable artifacts carry a stable identifier distinct from their name.
- 6 artifact(s) have a display label that diverges from the name a consumer must store.
- Identity is name-based: a rename is a breaking change discoverable only when stored references fail.

---
Framework: the machine-consumption contract from "The Machine-Consumption Contract of Business Intelligence: A Documentation Audit of Six Semantic Layers" by Vinuraj Devaraj.

Semantic Layer Contract Checker · Created by Vinuraj Devaraj, Independent Researcher
