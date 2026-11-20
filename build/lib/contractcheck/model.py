"""Normalized intermediate model for the Semantic Layer Contract Checker.

Every platform adapter parses its native project files into this model.
Platform specifics live only in the adapters; the scoring engine sees
only these structures.

An Artifact is anything a machine consumer can discover and build on:
a metric, a measure, a queryable model, or a command. Fields are named
for the contract elements they evidence (R1 to R10), not for any one
platform's vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Artifact:
    """One queryable artifact in the normalized model."""

    name: str
    kind: str  # "metric" | "measure" | "model" | "command"
    source: str  # where the adapter found it (manifest node id, file path)

    label: str | None = None
    description: str | None = None

    # R2 declared semantics (conjunctive: all four elements required)
    aggregation: str | None = None
    grain: str | None = None
    dimensions: list[str] = field(default_factory=list)
    time_behavior: str | None = None

    # R3 provenance and lineage
    lineage: list[str] = field(default_factory=list)  # upstream artifact names
    provenance_note: str | None = None

    # R4 freshness declaration a consumer can read
    freshness: str | None = None

    # R5 declared access (configuration evidence only)
    access: str | None = None

    # R6 certification
    owner: str | None = None
    certification: str | None = None

    # R7 result contract declarations
    unit: str | None = None
    caveats: str | None = None
    coverage_statement: str | None = None

    # R9 lifecycle signals
    deprecation: str | None = None
    version: str | None = None

    # R10 identity
    stable_id: str | None = None


@dataclass
class SourceArtifact:
    """An upstream data source declaration (dbt source, connector input)."""

    name: str
    source: str
    loaded_at_field: str | None = None
    freshness_thresholds: str | None = None  # e.g. "warn 12h, error 24h"
    description: str | None = None


@dataclass
class ContextEntry:
    """A reviewed shared-context entry: a business definition or assumption
    a team has saved for machine consumers (first-class in PromptQL)."""

    term: str
    definition: str
    source: str
    reviewed: bool = False
    kind: str = "definition"  # "definition" | "assumption" | "coverage"


@dataclass
class Project:
    """A whole semantic-layer project in normalized form."""

    platform: str  # "dbt" | "promptql"
    name: str
    artifacts: list[Artifact] = field(default_factory=list)
    sources: list[SourceArtifact] = field(default_factory=list)
    context_entries: list[ContextEntry] = field(default_factory=list)
    # Names of underlying (non-queryable) models, for lineage/deprecation locus checks
    underlying_models: list[Artifact] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def queryable(self) -> list[Artifact]:
        return self.artifacts
