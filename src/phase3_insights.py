"""Phase 3: explainability, resume improvement insights and project relevance.

All insights are derived from the parsed resume/JD and the configured skill
ontology. No generative model is used, so recommendations never invent
experience or achievements.
"""
import re
from typing import Callable, Dict, List, Optional

from src.skill_extractor import extract_skills
from src.skill_ontology import display


def _sentences(text: str) -> List[str]:
    """Return short evidence-sized text spans from resume content."""
    spans: List[str] = []
    for line in text.split("\n"):
        line = line.strip().lstrip("•●▪◦‣∙·*-–— ").strip()
        if not line:
            continue
        parts = re.split(r"(?<=[.!?;])\s+", line)
        spans.extend(p.strip() for p in parts if len(p.strip()) >= 8)
    return spans


def evidence_snippets(resume_text: str, max_per_skill: int = 2) -> Dict[str, List[str]]:
    """Map canonical skills to the resume sentences/bullets that mention them."""
    result: Dict[str, List[str]] = {}
    for span in _sentences(resume_text):
        for skill in extract_skills(span):
            bucket = result.setdefault(skill, [])
            if span not in bucket and len(bucket) < max_per_skill:
                bucket.append(span)
    return result


def rank_projects_phase3(
    projects: List[Dict],
    gap_items: List[Dict],
    jd_text: str,
    semantic_fn: Optional[Callable[[str, str], float]] = None,
    limit: int = 5,
) -> List[Dict]:
    """Rank projects using both job-skill overlap and semantic relevance."""
    if not projects:
        return []
    if semantic_fn is None:
        from src.embeddings import semantic_similarity as semantic_fn

    job_weight = {i["skill"]: i["weight"] for i in gap_items}
    ranked = []
    for project in projects:
        hits = sorted(project["skills"] & set(job_weight))
        if not hits:
            continue
        skill_overlap = sum(job_weight[s] for s in hits)
        total_job_weight = sum(job_weight.values()) or 1.0
        skill_score = skill_overlap / total_job_weight * 100
        semantic_score = max(0.0, min(100.0, semantic_fn(project["text"], jd_text) * 100))
        combined = 0.65 * skill_score + 0.35 * semantic_score
        ranked.append({
            "title": project["title"],
            "skills": [display(s) for s in hits],
            "skill_overlap": skill_score,
            "semantic_score": semantic_score,
            "score": combined,
        })
    ranked.sort(key=lambda p: (-p["score"], p["title"]))
    return ranked[:limit]


def improvement_plan(result: Dict) -> List[Dict]:
    """Create concrete, evidence-safe resume improvement actions."""
    gap = result["gap"]
    evidence = result["_resume"]["evidence"]
    plan: List[Dict] = []

    for item in gap["items"]:
        if item["status"] == "missing":
            requirement = item["requirement"]
            priority = "High" if requirement == "required" else "Medium"
            plan.append({
                "priority": priority,
                "skill": item["name"],
                "reason": f"{requirement.capitalize()} skill not detected in the resume.",
                "action": (
                    "If you genuinely have this skill, add a truthful project/experience bullet "
                    "showing how you used it; otherwise treat it as a learning target."
                ),
            })

    for item in gap["items"]:
        if item["status"] == "related":
            plan.append({
                "priority": "Medium",
                "skill": item["name"],
                "reason": f"Related evidence found: {', '.join(item['via'])}.",
                "action": "If the target skill was actually used, name it explicitly in the relevant project or experience bullet.",
            })

    for item in gap["items"]:
        if item["status"] == "matched" and item["evidence_level"] in ("listed", "mentioned"):
            plan.append({
                "priority": "Low",
                "skill": item["name"],
                "reason": "Detected, but the evidence is not in a project/experience context.",
                "action": "If truthful, strengthen the keyword with a concrete project, task, tool, or measurable result.",
            })

    # Remove duplicate skill recommendations while preserving priority order.
    seen = set()
    unique = []
    for item in plan:
        key = item["skill"]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:12]


def resume_quality_checks(resume: Dict) -> List[Dict]:
    """Simple structural checks; these are not a claim about any ATS vendor."""
    text = resume["text"]
    checks = []
    checks.append({
        "check": "Section structure",
        "status": "Pass" if resume["has_headings"] else "Review",
        "detail": "Recognized conventional resume headings." if resume["has_headings"] else "No conventional headings were detected; evidence weighting may be weaker.",
    })
    checks.append({
        "check": "Projects / experience evidence",
        "status": "Pass" if resume["projects"] or resume["sections"].get("experience") else "Review",
        "detail": "Project or experience content is available for evidence analysis." if (resume["projects"] or resume["sections"].get("experience")) else "Add project or experience evidence if applicable.",
    })
    email_ok = bool(re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", text))
    phone_ok = bool(re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", text))
    checks.append({
        "check": "Contact information",
        "status": "Pass" if email_ok and phone_ok else "Review",
        "detail": "Email and phone-like contact details detected." if email_ok and phone_ok else "Check that email and phone contact details are present and extractable.",
    })
    bullet_count = sum(1 for line in text.split("\n") if line.strip().startswith(("•", "-", "*")))
    checks.append({
        "check": "Bullet-based evidence",
        "status": "Pass" if bullet_count >= 3 else "Review",
        "detail": f"Detected approximately {bullet_count} bullet lines." if bullet_count >= 3 else "Few bullet lines detected; concise evidence bullets can improve scanability.",
    })
    return checks


def build_phase3_markdown(result: Dict, report: Dict, projects: List[Dict], plan: List[Dict], checks: List[Dict]) -> str:
    """Create a portable Markdown analysis report for download/GitHub demos."""
    gap = result["gap"]
    lines = [
        "# CareerMatch AI — Match Report",
        "",
        f"**Overall match:** {result['overall_score']:.1f}%  ",
        f"**Semantic similarity:** {result['semantic_score']:.1f}%  ",
        f"**Skill coverage:** {result['skill_score']:.1f}%  ",
        f"**Required coverage:** {gap['required_coverage']:.1f}%" if gap['required_coverage'] is not None else "**Required coverage:** n/a",
        "",
        "> This is an analytical signal from resume/JD text, not a hiring decision.",
        "",
        "## Summary",
        report["summary"],
        "",
        "## Priority improvement plan",
    ]
    if plan:
        for p in plan:
            lines.append(f"- **{p['priority']} — {p['skill']}**: {p['reason']} {p['action']}")
    else:
        lines.append("- No additional skill-focused actions were generated from the configured vocabulary.")
    lines += ["", "## Relevant projects"]
    if projects:
        for p in projects:
            lines.append(f"- **{p['title']}** — combined relevance {p['score']:.1f}%, skill overlap {p['skill_overlap']:.1f}%, semantic {p['semantic_score']:.1f}%. Skills: {', '.join(p['skills']) or 'none directly detected'}.")
    else:
        lines.append("- No project entries were available for ranking.")
    lines += ["", "## Resume quality checks"]
    for c in checks:
        lines.append(f"- **{c['status']} — {c['check']}**: {c['detail']}")
    return "\n".join(lines) + "\n"
