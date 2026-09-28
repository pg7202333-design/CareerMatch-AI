from src.sections import detect_jd_sections, detect_resume_sections, normalize_text, split_entries

RESUME = """Jane Doe
jane@example.com

EDUCATION
B.Tech, Example University

TECHNICAL SKILLS:
Python, SQL

Projects
Tool A
• Built a thing.
• Shipped it.
Tool B
• Built another thing.

Work Experience
Intern, Acme
• Did work.

Achievements & Awards
• Won a hackathon.
"""


def test_resume_sections_detected_with_heading_variants():
    sec = detect_resume_sections(RESUME)
    assert sec.has_headings
    assert sec.names() == ["education", "skills", "projects", "experience", "achievements"]
    assert "Jane Doe" in sec.get("header")
    assert "Python" in sec.get("skills")


def test_resume_without_headings_falls_back():
    sec = detect_resume_sections("Python developer with SQL experience.")
    assert not sec.has_headings
    assert list(sec.sections) == ["unsectioned"]
    assert sec.names() == []


def test_sentence_containing_heading_word_is_not_heading():
    sec = detect_resume_sections("Jane\nI enjoy working on projects with friends.\nSKILLS\nPython")
    assert sec.names() == ["skills"]


def test_jd_sections():
    jd = """ML Engineer
About us
We build things.
Responsibilities
- Train models
Required Qualifications:
Python
Nice to have
Docker
Benefits
Snacks"""
    sec = detect_jd_sections(jd)
    assert sec.names() == ["about", "responsibilities", "required", "preferred", "benefits"]
    assert sec.get("preferred") == "Docker"


def test_jd_prose_sentence_is_not_heading():
    sec = detect_jd_sections("Knowledge of NLP is preferred.\nPython is required.")
    assert not sec.has_headings


def test_split_entries_bulleted_titles():
    entries = split_entries("Tool A\n• Built a thing.\n• Shipped it.\nTool B\n• Built another thing.")
    assert [e["title"] for e in entries] == ["Tool A", "Tool B"]


def test_split_entries_blank_line_separated():
    entries = split_entries("Tool A\nDid this in Python\n\nTool B\nDid that in SQL")
    assert [e["title"] for e in entries] == ["Tool A", "Tool B"]


def test_normalize_joins_lone_bullets():
    assert normalize_text("•\nBuilt a model") == "• Built a model"
