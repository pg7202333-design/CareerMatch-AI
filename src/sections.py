"""Section detection for resumes and job descriptions, plus small text helpers."""
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

BULLET_CHARS = "•●▪◦‣∙·*-–—"

# ----------------------------------------------------------------------------
# Text helpers
# ----------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalise line endings/whitespace and re-attach bullets that PDFs put on their own line."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    text = re.sub(r"^[•●▪◦‣∙·]\s*\n\s*", "• ", text, flags=re.M)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def strip_bullet(line: str) -> str:
    return line.strip().lstrip(BULLET_CHARS + " ").strip()


def is_bullet(line: str) -> bool:
    s = line.strip()
    return bool(s) and s[0] in "•●▪◦‣∙·*" or bool(re.match(r"^[-–—]\s+\S", s))


def _norm(line: str) -> str:
    s = line.lower().replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z&/ ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _heading_candidate(line: str, max_chars: int, max_words: int) -> Optional[str]:
    s = line.strip()
    if not s or len(s) > max_chars or is_bullet(s):
        return None
    s = s.rstrip(":").strip()
    if s.endswith((".", ",", ";")) or len(s.split()) > max_words:
        return None
    return _norm(s)


@dataclass
class SectionResult:
    sections: Dict[str, str]
    has_headings: bool

    def names(self) -> List[str]:
        """Detected heading-based sections (excludes preamble / fallback buckets)."""
        return [k for k in self.sections if k not in ("header", "unsectioned")]

    def get(self, name: str, default: str = "") -> str:
        return self.sections.get(name, default)


def _split(text: str, classify, preamble_name: str) -> SectionResult:
    buckets: Dict[str, List[str]] = {}
    current = preamble_name
    found = False
    for line in text.split("\n"):
        name = classify(line)
        if name:
            found = True
            current = name
            buckets.setdefault(current, [])
            continue
        buckets.setdefault(current, []).append(line)
    if not found:
        return SectionResult({"unsectioned": text}, False)
    sections = {k: "\n".join(v).strip() for k, v in buckets.items()}
    sections = {k: v for k, v in sections.items() if v or k != preamble_name}
    return SectionResult(sections, True)


# ----------------------------------------------------------------------------
# Resume sections
# ----------------------------------------------------------------------------

_RESUME_HEADINGS = {
    "summary": ["summary", "professional summary", "career summary", "objective",
                "career objective", "profile", "professional profile", "about me"],
    "education": ["education", "academic background", "academics", "educational qualifications",
                  "academic qualifications", "education & training", "education and training"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "technologies",
               "tech stack", "technical proficiency", "skills & tools", "skills and tools",
               "areas of expertise", "technical expertise", "skills summary"],
    "projects": ["projects", "personal projects", "academic projects", "key projects",
                 "selected projects", "project experience", "technical projects"],
    "experience": ["experience", "work experience", "professional experience", "internships",
                   "internship experience", "internship", "employment history", "work history",
                   "relevant experience", "industrial experience", "internships & experience"],
    "achievements": ["achievements", "awards", "honors", "honours", "accomplishments",
                     "awards & achievements", "achievements & awards", "awards and achievements",
                     "achievements and awards", "honors & awards", "honors and awards",
                     "scholastic achievements"],
    "certifications": ["certifications", "certificates", "licenses & certifications",
                       "licenses and certifications", "courses", "courses & certifications",
                       "certifications & courses", "certifications and courses"],
    "extracurricular": ["extracurricular activities", "extracurriculars", "extra curricular activities",
                        "positions of responsibility", "leadership", "volunteering",
                        "volunteer experience", "activities"],
}
_RESUME_LOOKUP = {v: k for k, variants in _RESUME_HEADINGS.items() for v in variants}


def _classify_resume(line: str) -> Optional[str]:
    cand = _heading_candidate(line, max_chars=45, max_words=5)
    return _RESUME_LOOKUP.get(cand) if cand else None


def detect_resume_sections(text: str) -> SectionResult:
    """Split resume text into Education / Skills / Projects / Experience / Achievements / ...

    Text before the first heading is returned as ``header``. If no heading is
    recognised, everything is returned under ``unsectioned``.
    """
    return _split(text, _classify_resume, "header")


# ----------------------------------------------------------------------------
# Job-description sections
# ----------------------------------------------------------------------------

_JD_PREFERRED_START = ("preferred", "desired", "desirable", "bonus", "nice to have",
                       "good to have", "additional qualifications", "additional skills")
_JD_PREFERRED_EXACT = {"a plus", "its a plus", "pluses", "extra credit", "optional"}
_JD_REQUIRED_START = ("required", "minimum", "basic qualifications", "mandatory", "must have",
                      "essential")
_JD_REQUIRED_EXACT = {
    "requirements", "qualifications", "skills", "key skills", "technical skills",
    "skills & qualifications", "skills and qualifications", "skills and experience",
    "skills & experience", "experience", "eligibility", "eligibility criteria",
    "what you need", "what youll need", "what you will need", "what were looking for",
    "what we are looking for", "what we look for", "who you are", "you have",
    "you should have", "about you", "your profile", "candidate profile", "ideal candidate",
    "education & experience", "education and experience",
}
_JD_RESP_EXACT = {
    "responsibilities", "key responsibilities", "duties", "your responsibilities",
    "job responsibilities", "role and responsibilities", "roles & responsibilities",
    "roles and responsibilities", "what youll do", "what you will do", "what you will be doing",
    "what youll be doing", "the role", "your role", "about the role", "job description",
    "day to day", "in this role", "role overview", "position overview", "what you do",
}
_JD_ABOUT_START = ("about us", "about the company", "about the team", "who we are",
                   "company overview", "our mission", "overview")
_JD_BENEFITS_START = ("benefits", "perks", "what we offer", "compensation", "why join",
                      "why work", "salary", "what you get")


def _classify_jd(line: str) -> Optional[str]:
    cand = _heading_candidate(line, max_chars=60, max_words=8)
    if not cand:
        return None
    if cand in _JD_PREFERRED_EXACT or cand.startswith(_JD_PREFERRED_START):
        return "preferred"
    if cand in _JD_RESP_EXACT:
        return "responsibilities"
    if cand in _JD_REQUIRED_EXACT or cand.startswith(_JD_REQUIRED_START):
        return "required"
    if cand.startswith(_JD_BENEFITS_START):
        return "benefits"
    if cand.startswith(_JD_ABOUT_START):
        return "about"
    return None


def detect_jd_sections(text: str) -> SectionResult:
    """Split a job description into responsibilities / required / preferred / about / benefits."""
    return _split(text, _classify_jd, "header")


# ----------------------------------------------------------------------------
# Entry splitting (projects, experience)
# ----------------------------------------------------------------------------

def split_entries(text: str) -> List[Dict[str, str]]:
    """Split a Projects/Experience section into ``{"title", "text"}`` entries.

    Heuristic: a new entry starts after a blank line, or at a short capitalised
    non-bullet line that follows bullet content which ended a sentence. PDF line
    wrapping can still fool it; see the README limitations.
    """
    entries: List[List[str]] = []
    cur: List[str] = []
    cur_has_bullets = False
    prev = ""
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            if cur:
                entries.append(cur)
                cur, cur_has_bullets = [], False
            prev = ""
            continue
        bullet = is_bullet(s)
        title_like = (not bullet and len(s) <= 100 and s[0].isupper()
                      and not s.endswith((".", ",")))
        if title_like and cur and cur_has_bullets and prev.endswith((".", "!", "?", ")")):
            entries.append(cur)
            cur, cur_has_bullets = [], False
        cur.append(s)
        cur_has_bullets = cur_has_bullets or bullet
        prev = s
    if cur:
        entries.append(cur)
    return [{"title": strip_bullet(e[0]), "text": "\n".join(e)} for e in entries]
