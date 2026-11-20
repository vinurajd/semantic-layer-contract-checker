# Machine-Consumption Contract Scorecard — promptql

Platform: **promptql** · Supported: **1** · Reduced: **5** · Not documented: **3** · Not assessable: **1**

| Req | Requirement | Family | Verdict |
|-----|-------------|--------|---------|
| R1 | Enumerability of definitions | Definitions and declared semantics | documented as supported |
| R2 | Declared semantics | Definitions and declared semantics | documented with reduction |
| R3 | Provenance and lineage | Trust signals | documented with reduction |
| R4 | Freshness signals | Trust signals | not documented |
| R5 | Query-time access control | Enforcement and the exchange itself | documented with reduction |
| R6 | Certification | Trust signals | documented with reduction |
| R7 | Result contract | Enforcement and the exchange itself | not documented |
| R8 | Structured rejection | Enforcement and the exchange itself | not assessable |
| R9 | Deprecation and versioning signals | Identity and lifecycle | not documented |
| R10 | Stable identity | Identity and lifecycle | documented with reduction |

## Evidence by requirement

### R1 — Enumerability of definitions: documented as supported
- 3 queryable artifacts enumerated from the project's machine-readable surface (1 command, 2 model); discovery is a query, not a search through documents.

### R2 — Declared semantics: documented with reduction
- 0/3 queryable artifacts declare all four elements (aggregation, grain, dimensions, time behavior).
- TopCustomersByRevenue: missing aggregation, grain, dimensions, time behavior.
- Orders: missing grain, time behavior.
- Customers: missing aggregation, grain, time behavior.

### R3 — Provenance and lineage: documented with reduction
- 0/3 queryable artifacts carry machine-readable lineage to upstream artifacts.
- 0 upstream source(s) declared in the project.
- 1/3 artifacts carry a provenance note in their declaration.
- Underlying models with lineage: 0/2.
- 3 shared-context entr(ies) record reviewed definitions and assumptions; context is provenance-adjacent evidence and caps this cell at reduction on its own.

### R4 — Freshness signals: not documented
- No freshness declaration found on sources, artifacts, or shared context. Silence is coded as not documented, not as staleness.

### R5 — Query-time access control: documented with reduction
- 2/3 queryable artifacts carry an access declaration.
- Configuration evidence only: enforcement at query time against the caller's own machine identity is runtime behavior and is not assessable from project files, so this cell cannot be coded supported by a static audit.

### R6 — Certification: documented with reduction
- 0/3 queryable artifacts declare an owner.
- 0/3 carry a machine-readable certification or endorsement marker.
- 3 shared-context entr(ies) are marked reviewed; reviewed context is certification-adjacent evidence and caps this cell at reduction.

### R7 — Result contract: not documented
- Units declared: 0/3 artifacts. Grain declared: 0/3. Caveats or usage notes declared: 0/3.
- Scored on project declarations; whether the response payload itself carries units, grain, and caveats is runtime behavior and is not assessable from project files.
- Sub-check, coverage statement: declared (coverage): answers are required to state the population they represent.

### R8 — Structured rejection: not assessable
- Structured rejection is runtime behavior of the query surface: whether an invalid request receives an error an agent can act on cannot be evidenced by project files. Per the audit's honesty rule, this cell is reported as not assessable and is never silently scored; silence is not coded as refusal or as support.

### R9 — Deprecation and versioning signals: not documented
- 0/3 queryable artifacts carry a deprecation signal; 0/3 carry a version field.
- No deprecation signal or version field found in machine-readable form.

### R10 — Stable identity: documented with reduction
- 0/3 queryable artifacts carry a stable identifier distinct from their name.
- Identity is name-based: a rename is a breaking change discoverable only when stored references fail.

---
Framework: the machine-consumption contract from "The Machine-Consumption Contract of Business Intelligence: A Documentation Audit of Six Semantic Layers" by Vinuraj Devaraj.

Semantic Layer Contract Checker · Created by Vinuraj Devaraj, Independent Researcher
