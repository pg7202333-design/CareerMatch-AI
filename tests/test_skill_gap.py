from src.skill_gap import RELATED_CREDIT, analyze_gap


def _ev(**levels):
    return {k: {"sections": ["projects"], "level": v} for k, v in levels.items()}


def test_direct_related_missing_statuses():
    gap = analyze_gap(_ev(pytorch="demonstrated", python="listed"),
                      required={"python", "machine learning", "kubernetes"}, preferred=set())
    status = {i["skill"]: i["status"] for i in gap["items"]}
    assert status == {"python": "matched", "machine learning": "related", "kubernetes": "missing"}
    assert gap["missing_required"] == ["Kubernetes"]


def test_listed_only_earns_less_than_demonstrated():
    listed = analyze_gap(_ev(python="listed"), {"python"}, set())["coverage"]
    shown = analyze_gap(_ev(python="demonstrated"), {"python"}, set())["coverage"]
    assert shown == 100.0 and listed < shown


def test_related_credit_is_partial():
    gap = analyze_gap(_ev(tensorflow="demonstrated"), {"pytorch"}, set())
    assert gap["coverage"] == RELATED_CREDIT * 100


def test_required_weighs_more_than_preferred():
    ev = _ev(python="demonstrated")
    miss_required = analyze_gap(ev, {"python", "docker"}, set())["coverage"]
    miss_preferred = analyze_gap(ev, {"python"}, {"docker"})["coverage"]
    assert miss_preferred > miss_required


def test_required_skill_is_not_double_counted_as_preferred():
    gap = analyze_gap(_ev(), {"python"}, {"python"})
    assert len(gap["items"]) == 1


def test_empty_job_skills():
    gap = analyze_gap(_ev(python="demonstrated"), set(), set())
    assert not gap["has_job_skills"] and gap["coverage"] == 0.0
    assert gap["required_coverage"] is None
