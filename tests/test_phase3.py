from src.jd_parser import parse_job_description
from src.phase3_insights import evidence_snippets, rank_projects_phase3, resume_quality_checks
from src.resume_parser import parse_resume


def test_evidence_snippets_finds_skill_context():
    text = "Skills\nPython, SQL\nProjects\nBuilt a Python data pipeline using SQL."
    snippets = evidence_snippets(text)
    assert "python" in snippets
    assert any("Python" in s for s in snippets["python"])


def test_project_ranking_combines_skill_and_semantic_signal():
    resume = parse_resume("Projects\nAI Project\nBuilt a Python ML system.\n\nWeb Project\nBuilt HTML CSS pages.")
    jd = parse_job_description("Machine Learning intern\nRequired\nPython\nMachine Learning")
    fake_semantic = lambda a, b: 0.9 if "AI Project" in a else 0.1
    result = rank_projects_phase3(resume["projects"],
                                  [{"skill": "python", "weight": 1.0},
                                   {"skill": "machine learning", "weight": 1.0}],
                                  jd["core_text"], fake_semantic)
    assert result[0]["title"] == "AI Project"
    assert result[0]["semantic_score"] == 90.0


def test_quality_checks_return_structured_results():
    resume = parse_resume("Prachi Gupta\nEmail: p@example.com\nPhone: 9999999999\n\nSkills\nPython\n\nProjects\n- Built a Python app")
    checks = resume_quality_checks(resume)
    assert len(checks) == 4
    assert {c["check"] for c in checks} >= {"Section structure", "Contact information"}
