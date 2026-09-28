"""Hybrid matcher: semantic similarity + weighted skill coverage."""
from typing import Callable, Dict, Optional

from src.skill_gap import analyze_gap
from src.skill_ontology import display, weight
from src.phase3_insights import rank_projects_phase3

# Design choices, not universal optima. Raw MiniLM cosine scores for resume-vs-JD
# pairs sit in a narrow band, so explicit skill coverage gets the larger share.
W_SEMANTIC = 0.4
W_SKILL = 0.6


def rank_projects(projects, gap_items, limit: int = 3):
    """Rank resume projects by how many (weighted) job skills they demonstrate."""
    job_weight = {i["skill"]: i["weight"] for i in gap_items}
    ranked = []
    for project in projects:
        hits = sorted(project["skills"] & set(job_weight))
        if not hits:
            continue
        ranked.append({
            "title": project["title"],
            "skills": [display(s) for s in hits],
            "score": sum(job_weight[s] for s in hits),
        })
    ranked.sort(key=lambda p: (-p["score"], p["title"]))
    return ranked[:limit]


def calculate_match(resume: Dict, jd: Dict,
                    semantic_fn: Optional[Callable[[str, str], float]] = None,
                    w_semantic: float = W_SEMANTIC, w_skill: float = W_SKILL) -> Dict:
    """Score a parsed resume against a parsed JD.

    ``semantic_fn`` is injectable so tests can run without downloading a model.
    """
    if not (0 <= w_semantic <= 1 and 0 <= w_skill <= 1):
        raise ValueError("Scoring weights must be between 0 and 1.")
    if abs((w_semantic + w_skill) - 1.0) > 1e-9:
        raise ValueError("Semantic and skill weights must sum to 1.0.")
    if semantic_fn is None:
        from src.embeddings import semantic_similarity as semantic_fn
    warnings = []

    semantic_score = max(0.0, min(100.0, semantic_fn(resume["core_text"], jd["core_text"]) * 100))

    gap = analyze_gap(resume["evidence"], jd["required_skills"], jd["preferred_skills"])
    if gap["has_job_skills"]:
        skill_score = gap["coverage"]
        overall = w_semantic * semantic_score + w_skill * skill_score
    else:
        skill_score = 0.0
        overall = semantic_score
        warnings.append("No skills from the vocabulary were found in the job description, "
                        "so the score is semantic similarity only.")
    if not resume["has_headings"]:
        warnings.append("No resume section headings were detected; skill evidence strength "
                        "(projects vs. skills list) could not be assessed.")
    if not resume["skills"]:
        warnings.append("No skills from the vocabulary were detected in the resume.")

    return {
        "overall_score": overall,
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "weights": {"semantic": w_semantic, "skill": w_skill},
        "gap": gap,
        "projects": rank_projects_phase3(
            resume["projects"], gap["items"], jd["core_text"], semantic_fn=semantic_fn
        ),
        # flat lists kept for simple consumers
        "matched_skills": gap["matched"],
        "related_skills": gap["related"],
        "missing_skills": gap["missing_required"] + gap["missing_preferred"],
        "resume_skills": sorted(display(s) for s in resume["skills"]),
        "job_skills": sorted(display(s) for s in jd["all_skills"]),
        "resume_sections": resume["sections"].names(),
        "jd_sections": jd["sections"].names(),
        "warnings": warnings,
    }
