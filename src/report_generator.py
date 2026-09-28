"""Deterministic, evidence-grounded explanation of a match result.

Every sentence is generated from computed values (matched/related/missing
skills, evidence level, project overlap). No language model is involved, so the
report cannot state anything the analysis did not find.
"""
from typing import Dict, List


def _join(names: List[str], limit: int = 6) -> str:
    shown = names[:limit]
    extra = len(names) - len(shown)
    text = ", ".join(shown)
    return f"{text} (+{extra} more)" if extra > 0 else text


def _label(overall: float) -> str:
    if overall >= 75:
        return "strong"
    if overall >= 50:
        return "moderate"
    return "limited"


def build_report(result: Dict) -> Dict:
    gap = result["gap"]
    items = gap["items"]
    demonstrated = [i["name"] for i in items
                    if i["status"] == "matched" and i["evidence_level"] in ("demonstrated", "unsectioned")]
    listed_only = [i["name"] for i in items
                   if i["status"] == "matched" and i["evidence_level"] in ("listed", "mentioned")]
    related = [i for i in items if i["status"] == "related"]

    strengths, improvements = [], []
    if demonstrated:
        strengths.append(f"Skills shown in project/experience context: {_join(demonstrated)}.")
    if listed_only:
        strengths.append(f"Skills present, but only in a skills list or side mention: {_join(listed_only)}.")
    for r in related[:4]:
        strengths.append(f"{r['name']} is not stated directly, but related experience was found: "
                         f"{_join(r['via'], 3)}.")
    for p in result["projects"]:
        strengths.append(f"Project \"{p['title']}\" is relevant: it covers {_join(p['skills'])}.")

    if gap["missing_required"]:
        improvements.append(
            f"Required skills not detected: {_join(gap['missing_required'])}. If you genuinely have "
            "this experience, make it visible in a project or role; if not, treat these as learning targets.")
    if listed_only:
        verb = "appears" if len(listed_only) == 1 else "appear"
        improvements.append(
            f"{_join(listed_only, 4)} {verb} only as a keyword. Concrete evidence (what you built, "
            "with what result) would make it more convincing, if it exists.")
    if gap["missing_preferred"]:
        improvements.append(f"Preferred skills not detected: {_join(gap['missing_preferred'])}.")
    if not result["projects"]:
        improvements.append("No project entries overlapping with the job's skills were found.")

    overall = result["overall_score"]
    label = _label(overall)
    n_req_missing = len(gap["missing_required"])
    n_items = len(items)
    why_match = (
        f"{len(gap['matched'])} of {n_items} job skills were found directly"
        + (f" and {len(related)} more through related skills" if related else "")
        + f"; semantic similarity of the relevant resume sections to the job text is "
        f"{result['semantic_score']:.0f}%."
    ) if n_items else ("No vocabulary skills were found in the job description; only semantic "
                       f"similarity ({result['semantic_score']:.0f}%) is available.")
    why_not = (
        f"{n_req_missing} required skill(s) were not detected."
        if n_req_missing else "No required skills are missing from the configured vocabulary."
    )
    summary = (f"Overall alignment is {label} ({overall:.0f}/100). {why_match} {why_not} "
               "This is an analytical signal from text, not a judgement of ability.")
    return {"summary": summary, "why_match": why_match, "why_not": why_not,
            "strengths": strengths, "improvements": improvements, "label": label}


def build_explanation(result: Dict) -> str:
    """One-paragraph explanation (kept for backward compatibility)."""
    return build_report(result)["summary"]
