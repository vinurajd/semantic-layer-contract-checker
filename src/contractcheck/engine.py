"""Scoring engine: codes a normalized Project against R1 to R10.

The coding rules mirror the paper's audit rules:
- Four-value vocabulary: documented as supported; documented with
  reduction; not documented; not assessable (with the reason stated).
- Conjunctive requirements need every element for a supported coding.
- Silence is never coded as support or as refusal.
- Evidence found only on an authoring or operator surface, not on the
  consumption path, caps a cell at documented with reduction.
- Every cell names its deciding evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import Project

SUPPORTED = "documented as supported"
REDUCED = "documented with reduction"
NOT_DOCUMENTED = "not documented"
NOT_ASSESSABLE = "not assessable"

VERDICTS = (SUPPORTED, REDUCED, NOT_DOCUMENTED, NOT_ASSESSABLE)


@dataclass
class CellResult:
    requirement: str  # "R1" .. "R10"
    title: str
    family: str
    verdict: str
    evidence: list[str] = field(default_factory=list)
    sub_checks: list[tuple[str, str]] = field(default_factory=list)  # (name, finding)


@dataclass
class Scorecard:
    platform: str
    project_name: str
    cells: list[CellResult]

    def counts(self) -> dict[str, int]:
        c = {v: 0 for v in VERDICTS}
        for cell in self.cells:
            c[cell.verdict] += 1
        return c


def _frac(part: int, whole: int) -> str:
    return f"{part}/{whole}"


# ---------------------------------------------------------------- R1
def check_r1(p: Project) -> CellResult:
    arts = p.queryable()
    ev: list[str] = []
    if arts:
        kinds: dict[str, int] = {}
        for a in arts:
            kinds[a.kind] = kinds.get(a.kind, 0) + 1
        breakdown = ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()))
        ev.append(
            f"{len(arts)} queryable artifacts enumerated from the project's "
            f"machine-readable surface ({breakdown}); discovery is a query, "
            "not a search through documents."
        )
        return CellResult("R1", "Enumerability of definitions",
                          "Definitions and declared semantics",
                          SUPPORTED, ev)
    ev.append("No queryable artifacts could be enumerated from the project's "
              "machine-readable surface.")
    return CellResult("R1", "Enumerability of definitions",
                      "Definitions and declared semantics",
                      NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R2
R2_ELEMENTS = ("aggregation", "grain", "dimensions", "time_behavior")


def _r2_missing(a) -> list[str]:
    missing = []
    if not a.aggregation:
        missing.append("aggregation")
    if not a.grain:
        missing.append("grain")
    if not a.dimensions:
        missing.append("dimensions")
    if not a.time_behavior:
        missing.append("time behavior")
    return missing


def check_r2(p: Project) -> CellResult:
    """Conjunctive: every queryable artifact must declare all four
    elements (aggregation, grain, slicing dimensions, time behavior)
    for a supported coding."""
    arts = p.queryable()
    fam = "Definitions and declared semantics"
    title = "Declared semantics"
    if not arts:
        return CellResult("R2", title, fam, NOT_DOCUMENTED,
                          ["No queryable artifacts to assess."])
    complete = [a for a in arts if not _r2_missing(a)]
    any_element = [a for a in arts if len(_r2_missing(a)) < 4]
    ev = [f"{_frac(len(complete), len(arts))} queryable artifacts declare all "
          "four elements (aggregation, grain, dimensions, time behavior)."]
    for a in arts:
        m = _r2_missing(a)
        if m:
            ev.append(f"{a.name}: missing {', '.join(m)}.")
    if len(complete) == len(arts):
        return CellResult("R2", title, fam, SUPPORTED, ev)
    if any_element:
        return CellResult("R2", title, fam, REDUCED, ev)
    return CellResult("R2", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R3
def check_r3(p: Project) -> CellResult:
    fam = "Trust signals"
    title = "Provenance and lineage"
    arts = p.queryable()
    with_lineage = [a for a in arts if a.lineage]
    with_prov = [a for a in arts if a.provenance_note]
    sources_declared = len(p.sources)
    ev: list[str] = []
    if arts:
        ev.append(f"{_frac(len(with_lineage), len(arts))} queryable artifacts "
                  "carry machine-readable lineage to upstream artifacts.")
        ev.append(f"{sources_declared} upstream source(s) declared in the project.")
        if with_prov:
            ev.append(f"{_frac(len(with_prov), len(arts))} artifacts carry a "
                      "provenance note in their declaration.")
    models_with_lineage = [m for m in p.underlying_models if m.lineage]
    if p.underlying_models:
        ev.append(f"Underlying models with lineage: "
                  f"{_frac(len(models_with_lineage), len(p.underlying_models))}.")
    if p.context_entries:
        ev.append(f"{len(p.context_entries)} shared-context entr(ies) record "
                  "reviewed definitions and assumptions; context is "
                  "provenance-adjacent evidence and caps this cell at "
                  "reduction on its own.")
    if arts and len(with_lineage) == len(arts) and sources_declared:
        return CellResult("R3", title, fam, SUPPORTED, ev)
    if with_lineage or models_with_lineage or sources_declared or with_prov \
            or p.context_entries:
        return CellResult("R3", title, fam, REDUCED, ev)
    ev.append("No lineage, source declaration, or provenance note found.")
    return CellResult("R3", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R4
def check_r4(p: Project) -> CellResult:
    fam = "Trust signals"
    title = "Freshness signals"
    ev: list[str] = []
    src_full = [s for s in p.sources if s.loaded_at_field and s.freshness_thresholds]
    src_partial = [s for s in p.sources if s.loaded_at_field or s.freshness_thresholds]
    art_fresh = [a for a in p.queryable() if a.freshness]
    ctx_fresh = [c for c in p.context_entries if "fresh" in c.definition.lower()]
    if p.sources:
        ev.append(f"{_frac(len(src_full), len(p.sources))} source(s) declare both "
                  "a loaded-at field and freshness thresholds.")
    if art_fresh:
        ev.append(f"{len(art_fresh)} queryable artifact(s) carry a freshness "
                  "declaration of their own.")
    if ctx_fresh:
        ev.append(f"{len(ctx_fresh)} shared-context entr(ies) speak to freshness.")
    if src_full and len(src_full) == len(p.sources):
        return CellResult("R4", title, fam, SUPPORTED, ev)
    if src_partial or art_fresh or ctx_fresh:
        return CellResult("R4", title, fam, REDUCED, ev)
    ev.append("No freshness declaration found on sources, artifacts, or "
              "shared context. Silence is coded as not documented, not as "
              "staleness.")
    return CellResult("R4", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R5
def check_r5(p: Project) -> CellResult:
    """Access declarations are configuration evidence. Query-time
    enforcement against the caller's own identity is runtime behavior,
    so a static audit caps this cell at documented with reduction."""
    fam = "Enforcement and the exchange itself"
    title = "Query-time access control"
    arts = p.queryable()
    declared = [a for a in arts if a.access]
    models_declared = [m for m in p.underlying_models if m.access]
    ev: list[str] = []
    if arts:
        ev.append(f"{_frac(len(declared), len(arts))} queryable artifacts carry "
                  "an access declaration.")
    if models_declared:
        ev.append(f"{len(models_declared)} underlying model(s) carry access "
                  "declarations (authoring surface).")
    ev.append("Configuration evidence only: enforcement at query time against "
              "the caller's own machine identity is runtime behavior and is "
              "not assessable from project files, so this cell cannot be "
              "coded supported by a static audit.")
    if declared or models_declared:
        return CellResult("R5", title, fam, REDUCED, ev)
    ev.insert(0, "No access declaration found on any artifact.")
    return CellResult("R5", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R6
def check_r6(p: Project) -> CellResult:
    fam = "Trust signals"
    title = "Certification"
    arts = p.queryable()
    ev: list[str] = []
    with_owner = [a for a in arts if a.owner]
    with_cert = [a for a in arts if a.certification]
    reviewed_ctx = [c for c in p.context_entries if c.reviewed]
    if arts:
        ev.append(f"{_frac(len(with_owner), len(arts))} queryable artifacts "
                  "declare an owner.")
        ev.append(f"{_frac(len(with_cert), len(arts))} carry a machine-readable "
                  "certification or endorsement marker.")
    if reviewed_ctx:
        ev.append(f"{len(reviewed_ctx)} shared-context entr(ies) are marked "
                  "reviewed; reviewed context is certification-adjacent "
                  "evidence and caps this cell at reduction.")
    if arts and len(with_owner) == len(arts) and len(with_cert) == len(arts):
        return CellResult("R6", title, fam, SUPPORTED, ev)
    if with_owner or with_cert or reviewed_ctx:
        return CellResult("R6", title, fam, REDUCED, ev)
    ev.append("No owner, certification marker, or reviewed context found.")
    return CellResult("R6", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R7
def check_r7(p: Project) -> CellResult:
    """Conjunctive over units, grain, caveats, scored on what the project
    declares. The response payload itself is runtime behavior; the
    report states that the checker scores declarations."""
    fam = "Enforcement and the exchange itself"
    title = "Result contract"
    arts = p.queryable()
    ev: list[str] = []
    subs: list[tuple[str, str]] = []
    if not arts:
        return CellResult("R7", title, fam, NOT_DOCUMENTED,
                          ["No queryable artifacts to assess."])
    with_unit = [a for a in arts if a.unit]
    with_grain = [a for a in arts if a.grain]
    with_caveat = [a for a in arts if a.caveats]
    ev.append(f"Units declared: {_frac(len(with_unit), len(arts))} artifacts. "
              f"Grain declared: {_frac(len(with_grain), len(arts))}. "
              f"Caveats or usage notes declared: "
              f"{_frac(len(with_caveat), len(arts))}.")
    ev.append("Scored on project declarations; whether the response payload "
              "itself carries units, grain, and caveats is runtime behavior "
              "and is not assessable from project files.")
    # Coverage statement sub-check (named): does the project declare that
    # answers state the population they represent?
    cov_art = [a for a in arts if a.coverage_statement]
    cov_ctx = [c for c in p.context_entries if c.kind == "coverage"]
    if cov_art or cov_ctx:
        where = (cov_art[0].name if cov_art else cov_ctx[0].term)
        subs.append(("coverage statement",
                     f"declared ({where}): answers are required to state "
                     "the population they represent."))
    else:
        subs.append(("coverage statement",
                     "not documented: no declaration found that answers "
                     "state the population they represent."))
    full = len(arts)
    if (len(with_unit) == full and len(with_grain) == full
            and len(with_caveat) == full):
        return CellResult("R7", title, fam, SUPPORTED, ev, subs)
    if with_unit or with_grain or with_caveat:
        return CellResult("R7", title, fam, REDUCED, ev, subs)
    return CellResult("R7", title, fam, NOT_DOCUMENTED, ev, subs)


# ---------------------------------------------------------------- R8
def check_r8(p: Project) -> CellResult:
    fam = "Enforcement and the exchange itself"
    title = "Structured rejection"
    ev = ["Structured rejection is runtime behavior of the query surface: "
          "whether an invalid request receives an error an agent can act "
          "on cannot be evidenced by project files. Per the audit's "
          "honesty rule, this cell is reported as not assessable and is "
          "never silently scored; silence is not coded as refusal or as "
          "support."]
    return CellResult("R8", title, fam, NOT_ASSESSABLE, ev)


# ---------------------------------------------------------------- R9
def check_r9(p: Project) -> CellResult:
    fam = "Identity and lifecycle"
    title = "Deprecation and versioning signals"
    arts = p.queryable()
    ev: list[str] = []
    art_dep = [a for a in arts if a.deprecation]
    art_ver = [a for a in arts if a.version]
    mod_dep = [m for m in p.underlying_models if m.deprecation]
    if arts:
        ev.append(f"{_frac(len(art_dep), len(arts))} queryable artifacts carry "
                  "a deprecation signal; "
                  f"{_frac(len(art_ver), len(arts))} carry a version field.")
    if mod_dep:
        ev.append(f"{len(mod_dep)} underlying model(s) carry a deprecation "
                  "signal, one level below the artifacts a consumer "
                  "queries; that locus caps this cell at reduction.")
    if arts and len(art_dep) == len(arts):
        return CellResult("R9", title, fam, SUPPORTED, ev)
    if art_dep or art_ver or mod_dep:
        return CellResult("R9", title, fam, REDUCED, ev)
    ev.append("No deprecation signal or version field found in "
              "machine-readable form.")
    return CellResult("R9", title, fam, NOT_DOCUMENTED, ev)


# ---------------------------------------------------------------- R10
def check_r10(p: Project) -> CellResult:
    fam = "Identity and lifecycle"
    title = "Stable identity"
    arts = p.queryable()
    ev: list[str] = []
    if not arts:
        return CellResult("R10", title, fam, NOT_DOCUMENTED,
                          ["No queryable artifacts to assess."])
    with_id = [a for a in arts if a.stable_id]
    ev.append(f"{_frac(len(with_id), len(arts))} queryable artifacts carry a "
              "stable identifier distinct from their name.")
    labels = [a.label for a in arts if a.label]
    dup_labels = sorted({x for x in labels if labels.count(x) > 1})
    if dup_labels:
        ev.append(f"Rename-risk signal: duplicate display labels across "
                  f"artifacts: {', '.join(dup_labels)}.")
    divergent = [a for a in arts if a.label and a.label != a.name]
    if divergent:
        ev.append(f"{len(divergent)} artifact(s) have a display label that "
                  "diverges from the name a consumer must store.")
    if len(with_id) == len(arts):
        return CellResult("R10", title, fam, SUPPORTED, ev)
    ev.append("Identity is name-based: a rename is a breaking change "
              "discoverable only when stored references fail.")
    return CellResult("R10", title, fam, REDUCED, ev)


CHECKS = (check_r1, check_r2, check_r3, check_r4, check_r5,
          check_r6, check_r7, check_r8, check_r9, check_r10)


def score_project(p: Project) -> Scorecard:
    return Scorecard(platform=p.platform, project_name=p.name,
                     cells=[fn(p) for fn in CHECKS])
