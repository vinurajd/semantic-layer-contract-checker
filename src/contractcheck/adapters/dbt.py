"""dbt adapter: parses a dbt manifest.json into the normalized model.

Reads semantic models (measures, dimensions, entities), metrics, model
nodes (lineage, access, deprecation), and source declarations (freshness)
from the manifest. Platform specifics live here only.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..model import Artifact, Project, SourceArtifact


def _short_name(unique_id: str) -> str:
    """model.my_project.orders -> orders; metric.my_project.revenue -> revenue"""
    parts = unique_id.split(".")
    return parts[-1] if parts else unique_id


def _ref_name(ref: str | None) -> str | None:
    """A semantic model's model field looks like ref('orders')."""
    if not ref:
        return None
    if "ref(" in ref:
        inner = ref.split("'", 2)
        return inner[1] if len(inner) > 1 else ref
    return _short_name(ref)


def _freshness_text(fresh: dict | None) -> str | None:
    if not fresh:
        return None
    bits = []
    for key, label in (("warn_after", "warn"), ("error_after", "error")):
        spec = fresh.get(key)
        if spec and spec.get("count") is not None:
            bits.append(f"{label} after {spec['count']} {spec.get('period', '')}".strip())
    return ", ".join(bits) if bits else None


def _certification(meta: dict, tags: list) -> str | None:
    for key in ("certified", "verified", "endorsed"):
        if meta.get(key):
            return f"meta.{key} = {meta[key]}"
    for tag in tags or []:
        if "certif" in str(tag).lower() or "verified" in str(tag).lower():
            return f"tag: {tag}"
    return None


def load_project(path: str | Path) -> Project:
    path = Path(path)
    manifest_path = path
    if path.is_dir():
        for candidate in (path / "target" / "manifest.json", path / "manifest.json"):
            if candidate.exists():
                manifest_path = candidate
                break
        else:
            raise FileNotFoundError(
                f"No manifest.json found under {path} "
                "(looked in target/manifest.json and manifest.json).")
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)

    project_name = (manifest.get("metadata") or {}).get("project_name") or "dbt project"
    project = Project(platform="dbt", name=project_name)

    nodes = manifest.get("nodes") or {}

    # ---- underlying models (lineage, access, deprecation locus)
    for uid, node in nodes.items():
        if node.get("resource_type") != "model":
            continue
        config = node.get("config") or {}
        meta = node.get("meta") or {}
        deps = [(_short_name(d)) for d in (node.get("depends_on") or {}).get("nodes", [])]
        project.underlying_models.append(Artifact(
            name=node.get("name") or _short_name(uid),
            kind="model",
            source=uid,
            label=node.get("label"),
            description=node.get("description") or None,
            lineage=deps,
            access=config.get("access") or None,
            owner=meta.get("owner") or config.get("group") or None,
            deprecation=node.get("deprecation_date") or meta.get("deprecation_date") or None,
            version=(node.get("version") if node.get("version") is not None else None),
        ))
    model_names = {m.name for m in project.underlying_models}

    # ---- sources (freshness)
    for uid, src in (manifest.get("sources") or {}).items():
        project.sources.append(SourceArtifact(
            name=f"{src.get('source_name', '')}.{src.get('name', '')}".strip("."),
            source=uid,
            loaded_at_field=src.get("loaded_at_field") or None,
            freshness_thresholds=_freshness_text(src.get("freshness")),
            description=src.get("description") or None,
        ))

    # ---- semantic models: measures and dimensions
    measures: dict[str, Artifact] = {}
    for uid, sm in (manifest.get("semantic_models") or {}).items():
        dims = sm.get("dimensions") or []
        dim_names = [d.get("name") for d in dims if d.get("name")]
        time_dims = {d.get("name"): (d.get("type_params") or {}).get("time_granularity")
                     for d in dims if d.get("type") == "time"}
        default_time_dim = (sm.get("defaults") or {}).get("agg_time_dimension")
        model_ref = _ref_name(sm.get("model"))
        for meas in sm.get("measures") or []:
            time_dim = meas.get("agg_time_dimension") or default_time_dim
            grain = time_dims.get(time_dim) if time_dim else None
            measures[meas.get("name")] = Artifact(
                name=meas.get("name"),
                kind="measure",
                source=uid,
                label=meas.get("label"),
                description=meas.get("description") or None,
                aggregation=meas.get("agg") or None,
                grain=grain,
                dimensions=list(dim_names),
                time_behavior=(f"aggregated over time dimension '{time_dim}'"
                               if time_dim else None),
                lineage=[model_ref] if model_ref in model_names or model_ref else [],
            )

    # ---- metrics
    for uid, met in (manifest.get("metrics") or {}).items():
        meta = met.get("meta") or {}
        config_meta = ((met.get("config") or {}).get("meta") or {})
        meta = {**config_meta, **meta}
        tp = met.get("type_params") or {}
        mtype = met.get("type")
        aggregation = None
        time_behavior = None
        grain = None
        dims: list[str] = []
        lineage: list[str] = []
        measure_names: list[str] = []
        if mtype == "simple":
            measure_names = [((tp.get("measure") or {}).get("name"))]
        elif mtype == "ratio":
            measure_names = [((tp.get("numerator") or {}).get("name")),
                             ((tp.get("denominator") or {}).get("name"))]
            aggregation = "ratio"
        elif mtype in ("cumulative",):
            measure_names = [((tp.get("measure") or {}).get("name"))]
            window = tp.get("window")
            gtd = tp.get("grain_to_date")
            time_behavior = "cumulative"
            if window:
                time_behavior += f" (window {window})"
            if gtd:
                time_behavior += f" (grain to date {gtd})"
                grain = gtd
        elif mtype == "derived":
            time_behavior = "derived from other metrics"
            aggregation = "derived expression"
        elif mtype == "conversion":
            measure_names = [((tp.get("base_measure") or {}).get("name")),
                             ((tp.get("conversion_measure") or {}).get("name"))]
            aggregation = "conversion"
        for mname in measure_names:
            meas = measures.get(mname)
            if meas is None:
                continue
            if aggregation is None:
                aggregation = meas.aggregation
            if grain is None:
                grain = meas.grain
            if time_behavior is None:
                time_behavior = meas.time_behavior
            dims = dims or list(meas.dimensions)
            lineage = lineage or list(meas.lineage)
        project.artifacts.append(Artifact(
            name=met.get("name") or _short_name(uid),
            kind="metric",
            source=uid,
            label=met.get("label"),
            description=met.get("description") or None,
            aggregation=aggregation,
            grain=grain,
            dimensions=dims,
            time_behavior=time_behavior,
            lineage=lineage,
            owner=meta.get("owner"),
            certification=_certification(meta, met.get("tags") or []),
            unit=meta.get("unit"),
            caveats=meta.get("caveats") or meta.get("usage_notes"),
            coverage_statement=meta.get("coverage_statement"),
            deprecation=meta.get("deprecation_date") or meta.get("deprecation"),
            version=str(met["version"]) if met.get("version") is not None else None,
        ))

    # Measures are queryable artifacts too (they are what metrics compose).
    project.artifacts.extend(measures.values())
    return project
