"""Resume understanding: sections, per-skill evidence, project entries."""
from typing import Dict, List

from src.sections import detect_resume_sections, normalize_text, split_entries
from src.skill_extractor import extract_skills
from src.skill_ontology import IMPLIES

# Sections whose content is used for the semantic comparison.
_CORE_SECTIONS = ("summary", "skills", "projects", "experience", "achievements", "certifications")


def _evidence_level(sections: List[str], has_headings: bool) -> str:
    """How convincingly a skill is shown.

    demonstrated: appears in Projects/Experience (used in context)
    listed:       appears in a Skills list only
    mentioned:    appears elsewhere (summary, education, achievements, ...)
    unsectioned:  the resume has no detectable headings, so we cannot tell
    """
    if not has_headings:
        return "unsectioned"
    if "projects" in sections or "experience" in sections:
        return "demonstrated"
    if "skills" in sections:
        return "listed"
    return "mentioned"


def _upgrade_by_implication(evidence: Dict[str, Dict]) -> None:
    """A skill that is only listed counts as demonstrated when a skill used in a
    project/experience implies it (e.g. K-Means in a project evidences Machine Learning;
    pandas in a project evidences Python). The skill must still be stated somewhere."""
    for skill, info in evidence.items():
        if info["level"] not in ("listed", "mentioned"):
            continue
        by = sorted(s for s, i in evidence.items()
                    if i["level"] == "demonstrated" and skill in IMPLIES.get(s, ()))
        if by:
            info["level"] = "demonstrated"
            info["implied_by"] = by


def parse_resume(text: str) -> Dict:
    text = normalize_text(text)
    sec = detect_resume_sections(text)

    evidence: Dict[str, Dict] = {}
    for name, body in sec.sections.items():
        for skill in extract_skills(body):
            evidence.setdefault(skill, {"sections": []})["sections"].append(name)
    for info in evidence.values():
        info["level"] = _evidence_level(info["sections"], sec.has_headings)

    _upgrade_by_implication(evidence)

    projects = []
    for entry in split_entries(sec.get("projects")):
        projects.append({
            "title": entry["title"],
            "text": entry["text"],
            "skills": extract_skills(entry["text"]),
        })

    if sec.has_headings:
        core = "\n".join(sec.get(n) for n in _CORE_SECTIONS if sec.get(n)) or text
    else:
        core = text

    return {
        "text": text,
        "sections": sec,
        "has_headings": sec.has_headings,
        "skills": extract_skills(text),
        "evidence": evidence,
        "projects": projects,
        "core_text": core,
    }
