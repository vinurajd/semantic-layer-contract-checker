"""Engine coding-rule tests: conjunctive requirements, silence handling,
the not-assessable path, and the locus caps."""

from contractcheck import engine
from contractcheck.model import Artifact, ContextEntry, Project, SourceArtifact


def make_project(**kwargs) -> Project:
    base = dict(platform="dbt", name="t")
    base.update(kwargs)
    return Project(**base)


def full_artifact(name="m") -> Artifact:
    return Artifact(
        name=name, kind="metric", source="test",
        aggregation="sum", grain="day", dimensions=["region"],
        time_behavior="aggregated over time dimension 'd'",
        lineage=["model_a"], owner="team", certification="meta.certified = True",
        unit="USD", caveats="Excludes refunds.", deprecation="2027-01-01",
        stable_id="urn:metric:1",
    )


def cell(sc, req):
    return next(c for c in sc.cells if c.requirement == req)


def test_r2_conjunctive_all_elements_supported():
    sc = engine.score_project(make_project(artifacts=[full_artifact()]))
    assert cell(sc, "R2").verdict == engine.SUPPORTED


def test_r2_conjunctive_one_missing_element_is_reduction():
    a = full_artifact()
    a.grain = None
    sc = engine.score_project(make_project(artifacts=[a]))
    c = cell(sc, "R2")
    assert c.verdict == engine.REDUCED
    assert any("grain" in e for e in c.evidence)


def test_r2_no_elements_is_not_documented():
    a = Artifact(name="bare", kind="metric", source="test")
    sc = engine.score_project(make_project(artifacts=[a]))
    assert cell(sc, "R2").verdict == engine.NOT_DOCUMENTED


def test_silence_is_not_documented_never_support_or_refusal():
    sc = engine.score_project(make_project())
    assert cell(sc, "R1").verdict == engine.NOT_DOCUMENTED
    assert cell(sc, "R4").verdict == engine.NOT_DOCUMENTED
    for c in sc.cells:
        assert "refused" not in c.verdict


def test_r8_always_not_assessable_with_reason():
    sc = engine.score_project(make_project(artifacts=[full_artifact()]))
    c = cell(sc, "R8")
    assert c.verdict == engine.NOT_ASSESSABLE
    assert any("runtime" in e for e in c.evidence)


def test_r5_configuration_evidence_capped_at_reduction():
    a = full_artifact()
    a.access = "protected"
    sc = engine.score_project(make_project(artifacts=[a]))
    assert cell(sc, "R5").verdict == engine.REDUCED


def test_r9_deprecation_on_underlying_model_only_is_reduction():
    a = full_artifact()
    a.deprecation = None
    model = Artifact(name="model_a", kind="model", source="test",
                     deprecation="2026-06-30")
    sc = engine.score_project(make_project(artifacts=[a],
                                           underlying_models=[model]))
    assert cell(sc, "R9").verdict == engine.REDUCED


def test_r4_partial_freshness_is_reduction():
    src = SourceArtifact(name="raw.orders", source="s1",
                         loaded_at_field="_loaded_at")
    sc = engine.score_project(make_project(sources=[src]))
    assert cell(sc, "R4").verdict == engine.REDUCED


def test_r7_coverage_subcheck_declared_and_absent():
    a = full_artifact()
    a.coverage_statement = "Answers state the population they represent."
    sc = engine.score_project(make_project(artifacts=[a]))
    subs = dict(cell(sc, "R7").sub_checks)
    assert "declared" in subs["coverage statement"]
    sc2 = engine.score_project(make_project(artifacts=[full_artifact()]))
    subs2 = dict(cell(sc2, "R7").sub_checks)
    assert "not documented" in subs2["coverage statement"]


def test_counts_sum_to_ten():
    sc = engine.score_project(make_project(artifacts=[full_artifact()]))
    assert sum(sc.counts().values()) == 10


def test_reviewed_context_caps_r6_at_reduction():
    ctx = ContextEntry(term="revenue", definition="...", source="c",
                       reviewed=True)
    sc = engine.score_project(make_project(context_entries=[ctx]))
    assert cell(sc, "R6").verdict == engine.REDUCED
