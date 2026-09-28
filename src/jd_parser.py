"""Job-description understanding: sections, responsibilities, required vs preferred skills."""
import re
from typing import Dict, List, Set

from src.sections import detect_jd_sections, normalize_text, strip_bullet
from src.skill_extractor import extract_skills

_PREFERRED_CUES = re.compile(
    r"\b(preferred|nice to have|good to have|a plus|plus point|bonus|desirable|desired|"
    r"advantage|an asset|useful|helpful|beneficial|ideally|would be great)\b",
    re.I,
)

# Sections that describe the company or perks, not the candidate.
_IGNORED_SECTIONS = ("about", "benefits")


def split_statements(text: str) -> List[str]:
    """Split text into bullet/sentence-sized statements."""
    statements = []
    for line in text.split("\n"):
        line = strip_bullet(line)
        for part in re.split(r"(?<=[.!?;])\s+", line):
            part = part.strip()
            if len(part) > 2:
                statements.append(part)
    return statements


def _looks_like_title(first_line: str, has_more: bool) -> bool:
    s = first_line.strip()
    return bool(s) and has_more and len(s) <= 80 and len(s.split()) <= 10 and not s.endswith(".")


def parse_job_description(text: str) -> Dict:
    """Parse a JD into structured parts.

    Skills are classified per statement: a statement in a Preferred section, or
    containing a preferred cue ("is a plus", "nice to have", ...), yields
    *preferred* skills; everything else in a candidate-facing section is
    *required*. A skill that is both required and preferred counts as required.
    """
    text = normalize_text(text)
    sec = detect_jd_sections(text)

    title = ""
    lines = text.split("\n")
    if _looks_like_title(lines[0], len(lines) > 1):
        title = lines[0].strip()

    required: Set[str] = set()
    preferred: Set[str] = set()
    responsibilities: List[str] = []
    required_quals: List[str] = []
    preferred_quals: List[str] = []
    core_parts: List[str] = []

    for name, body in sec.sections.items():
        if name in _IGNORED_SECTIONS:
            continue
        if name == "header" and sec.has_headings:
            body = body if body.strip() != title else ""
        elif name == "unsectioned" and title:
            body = "\n".join(body.split("\n")[1:])
        if not body.strip():
            continue
        core_parts.append(body)

        for stmt in split_statements(body):
            skills = extract_skills(stmt)
            is_pref = name == "preferred" or _PREFERRED_CUES.search(stmt) is not None
            if name == "responsibilities":
                responsibilities.append(stmt)
            elif is_pref:
                preferred_quals.append(stmt)
            else:
                required_quals.append(stmt)
            (preferred if is_pref else required).update(skills)

    if title:
        required.update(extract_skills(title))
    preferred -= required

    return {
        "title": title,
        "sections": sec,
        "has_headings": sec.has_headings,
        "responsibilities": responsibilities,
        "required_qualifications": required_quals,
        "preferred_qualifications": preferred_quals,
        "required_skills": required,
        "preferred_skills": preferred,
        "all_skills": required | preferred,
        "core_text": "\n".join(([title] if title else []) + core_parts) or text,
    }
