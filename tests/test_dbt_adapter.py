from pathlib import Path

from contractcheck.adapters import dbt

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "dbt" / "manifest.json"


def load():
    return dbt.load_project(FIXTURE)


def test_project_and_artifact_counts():
    p = load()
    assert p.platform == "dbt"
    assert p.name == "northwind_analytics"
    # 3 metrics + 3 measures
    assert len(p.artifacts) == 6
    assert len(p.underlying_models) == 3
    assert len(p.sources) == 2


def test_metric_inherits_measure_semantics():
    p = load()
    rev = next(a for a in p.artifacts if a.name == "total_revenue")
    assert rev.aggregation == "sum"
    assert rev.grain == "day"
    assert "region" in rev.dimensions
    assert rev.time_behavior is not None
    assert rev.unit == "USD"
    assert rev.owner == "analytics-team"
    assert rev.lineage == ["orders"]


def test_measure_without_time_dimension_is_incomplete():
    p = load()
    disc = next(a for a in p.artifacts if a.name == "discount_total")
    assert disc.aggregation == "sum"
    assert disc.grain is None
    assert disc.time_behavior is None


def test_freshness_parsing_full_and_partial():
    p = load()
    orders = next(s for s in p.sources if s.name == "raw.orders")
    payments = next(s for s in p.sources if s.name == "raw.payments")
    assert orders.loaded_at_field == "_loaded_at"
    assert orders.freshness_thresholds and "warn" in orders.freshness_thresholds
    assert payments.loaded_at_field == "_loaded_at"
    assert payments.freshness_thresholds is None


def test_model_access_and_deprecation():
    p = load()
    orders = next(m for m in p.underlying_models if m.name == "orders")
    assert orders.access == "protected"
    assert orders.deprecation == "2026-06-30"
    assert orders.lineage == ["stg_orders"]
