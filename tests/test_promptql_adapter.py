from pathlib import Path

from contractcheck.adapters import promptql

FIXTURE = (Path(__file__).resolve().parents[1] / "examples" / "promptql"
           / "metadata")


def load():
    return promptql.load_project(FIXTURE)


def test_artifacts_and_context_counts():
    p = load()
    assert p.platform == "promptql"
    assert {a.name for a in p.artifacts} == {
        "Orders", "Customers", "TopCustomersByRevenue"}
    assert len(p.context_entries) == 3


def test_model_dimensions_from_fields_and_relationships():
    p = load()
    orders = next(a for a in p.artifacts if a.name == "Orders")
    assert "region" in orders.dimensions          # ObjectType field
    assert "Customer" in orders.dimensions        # Relationship slicing path
    assert orders.aggregation is not None         # aggregate declared


def test_permissions_attach_as_access():
    p = load()
    orders = next(a for a in p.artifacts if a.name == "Orders")
    cmd = next(a for a in p.artifacts if a.name == "TopCustomersByRevenue")
    assert orders.access and "analyst" in orders.access
    assert cmd.access and "analyst" in cmd.access


def test_coverage_context_entry():
    p = load()
    cov = [c for c in p.context_entries if c.kind == "coverage"]
    assert len(cov) == 1
    assert cov[0].reviewed is True
    assert "population" in cov[0].definition


def test_glossary_entry_becomes_provenance_note():
    p = load()
    cmd = next(a for a in p.artifacts if a.name == "TopCustomersByRevenue")
    assert cmd.provenance_note is not None
    assert "net of refunds" in cmd.provenance_note
