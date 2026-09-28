"""Rule-based skill extraction on top of the skill ontology."""
import re
from typing import Dict, List, Set

from src.skill_ontology import IMPLIES, SIBLINGS, SKILLS

# A skill token must not be glued to word characters, dots, '+' or '#'
# ("Node.js" must not yield "js"; "C++" must not yield "C"; "python3" is handled by an alias).
_LEFT = r"(?<![\w.+#])"
_RIGHT = r"(?![\w+#])"

# URLs, e-mail addresses and bare domains are removed first, so that
# "github.com/user" is not read as a claim of GitHub skill.
_NOISE = re.compile(
    r"(?:https?://|www\.)\S+|\S+@\S+|\b[\w.-]+\.(?:com|io|org|net|dev)(?:/\S*)?",
    re.I,
)


def _compile() -> Dict[str, List[re.Pattern]]:
    compiled = {}
    for canonical, (_, _, aliases) in SKILLS.items():
        patterns = []
        for alias in aliases:
            if alias.startswith("cs:"):
                patterns.append(re.compile(_LEFT + re.escape(alias[3:]) + _RIGHT))
            else:
                patterns.append(re.compile(_LEFT + re.escape(alias) + _RIGHT, re.I))
        compiled[canonical] = patterns
    return compiled


_PATTERNS = _compile()


def extract_skills(text: str) -> Set[str]:
    """Return the set of canonical skill keys mentioned in ``text``."""
    text = _NOISE.sub(" ", text)
    return {
        canonical
        for canonical, patterns in _PATTERNS.items()
        if any(p.search(text) for p in patterns)
    }


def related_evidence(resume_skills: Set[str], job_skill: str) -> List[str]:
    """Resume skills that count as *related* (not identical) evidence for ``job_skill``."""
    evidence = set()
    for skill in resume_skills:
        if skill == job_skill:
            continue
        if job_skill in IMPLIES.get(skill, ()) or skill in SIBLINGS.get(job_skill, ()):
            evidence.add(skill)
    return sorted(evidence)


def find_related_skills(resume_skills: Set[str], job_skills: Set[str]) -> Set[str]:
    """Job skills that are not directly present but have related evidence in the resume."""
    return {
        job_skill
        for job_skill in job_skills
        if job_skill not in resume_skills and related_evidence(resume_skills, job_skill)
    }
