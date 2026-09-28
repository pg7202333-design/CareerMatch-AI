"""Weighted skill-gap analysis: required vs preferred, direct vs related, evidence-aware."""
from typing import Dict, Set

from src.skill_extractor import related_evidence
from src.skill_ontology import display, weight

REQUIREMENT_WEIGHT = {"required": 1.0, "preferred": 0.5}
RELATED_CREDIT = 0.5
EVIDENCE_CREDIT = {"demonstrated": 1.0, "listed": 0.8, "mentioned": 0.7, "unsectioned": 1.0}


def _coverage(items, requirement=None):
    pool = [i for i in items if requirement is None or i["requirement"] == requirement]
    total = sum(i["weight"] for i in pool)
    if not total:
        return None
    return sum(i["weight"] * i["credit"] for i in pool) / total * 100


def analyze_gap(evidence: Dict[str, Dict], required: Set[str], preferred: Set[str]) -> Dict:
    """Compare resume skill evidence against required/preferred job skills.

    Credit per job skill: direct match 0.7-1.0 depending on how well the resume
    shows it (see EVIDENCE_CREDIT), related match 0.5, missing 0. Each skill is
    weighted by requirement level (required 1.0, preferred 0.5) times an
    importance weight from its category. Every concept appears once.
    """
    resume_skills = set(evidence)
    items = []
    for requirement, skills in (("required", required), ("preferred", preferred - required)):
        for skill in skills:
            w = REQUIREMENT_WEIGHT[requirement] * weight(skill)
            item = {"skill": skill, "name": display(skill), "requirement": requirement,
                    "weight": w, "via": [], "evidence_level": None}
            if skill in resume_skills:
                level = evidence[skill]["level"]
                item.update(status="matched", credit=EVIDENCE_CREDIT[level], evidence_level=level,
                            found_in=list(evidence[skill]["sections"]))
            else:
                via = related_evidence(resume_skills, skill)
                if via:
                    item.update(status="related", credit=RELATED_CREDIT,
                                via=[display(v) for v in via])
                else:
                    item.update(status="missing", credit=0.0)
            items.append(item)

    order = {"required": 0, "preferred": 1}
    status_order = {"matched": 0, "related": 1, "missing": 2}
    items.sort(key=lambda i: (order[i["requirement"]], status_order[i["status"]],
                              -i["weight"], i["name"]))

    def names(status, requirement=None):
        return [i["name"] for i in items
                if i["status"] == status and (requirement is None or i["requirement"] == requirement)]

    coverage = _coverage(items)
    return {
        "items": items,
        "coverage": coverage if coverage is not None else 0.0,
        "has_job_skills": bool(items),
        "required_coverage": _coverage(items, "required"),
        "preferred_coverage": _coverage(items, "preferred"),
        "matched": names("matched"),
        "related": names("related"),
        "missing_required": names("missing", "required"),
        "missing_preferred": names("missing", "preferred"),
    }
