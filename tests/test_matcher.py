from src.pipeline import analyze
from src.report_generator import build_explanation, build_report

RESUME = """Aarav Mehta
EDUCATION
B.Tech CS
TECHNICAL SKILLS
Python, SQL, PyTorch, Git
PROJECTS
Resume Screener
• Built an NLP pipeline with sentence embeddings in Python.
• Deployed with Docker.
Weather Dashboard
• Built a Flask app.
EXPERIENCE
Data Intern
• Preprocessed data with pandas.
"""

JD = """AI/ML Intern
We are looking for a student with Python and machine learning experience.
Knowledge of NLP, embeddings and Kubernetes is preferred.
"""


def fake_semantic(a, b):
    return 0.5


def test_pipeline_scores_and_flat_keys():
    r = analyze(RESUME, JD, semantic_fn=fake_semantic)
    assert r["semantic_score"] == 50.0
    assert 0 <= r["overall_score"] <= 100
    w = r["weights"]
    expected = w["semantic"] * 50.0 + w["skill"] * r["skill_score"]
    assert abs(r["overall_score"] - expected) < 1e-9
    assert "Python" in r["matched_skills"]
    assert "Machine Learning" in r["related_skills"]      # via PyTorch
    assert r["missing_skills"] == ["Kubernetes"]
    assert r["resume_sections"] == ["education", "skills", "projects", "experience"]


def test_relevant_project_ranking():
    r = analyze(RESUME, JD, semantic_fn=fake_semantic)
    assert r["projects"][0]["title"] == "Resume Screener"
    assert "Embeddings" in r["projects"][0]["skills"]
    assert all(p["title"] != "Weather Dashboard" for p in r["projects"])


def test_no_job_skills_falls_back_to_semantic_only():
    r = analyze(RESUME, "We want a great team player.", semantic_fn=fake_semantic)
    assert r["overall_score"] == r["semantic_score"]
    assert any("semantic similarity only" in w for w in r["warnings"])


def test_unsectioned_resume_warns_and_still_scores():
    r = analyze("Python and SQL developer", JD, semantic_fn=fake_semantic)
    assert any("section headings" in w for w in r["warnings"])
    assert "Python" in r["matched_skills"]


def test_report_is_grounded_in_result():
    r = analyze(RESUME, JD, semantic_fn=fake_semantic)
    report = build_report(r)
    assert not any("Kubernetes" in s for s in report["strengths"])
    assert "Resume Screener" in " ".join(report["strengths"])
    assert build_explanation(r) == report["summary"]
    assert "not a judgement of ability" in report["summary"]


def test_listed_skill_is_demonstrated_when_project_skill_implies_it():
    from src.resume_parser import parse_resume
    text = ("SKILLS\nPython, Machine Learning\nPROJECTS\nChurn Model\n"
            "• Clustered customers with K-Means using pandas.\n")
    ev = parse_resume(text)["evidence"]
    assert ev["machine learning"]["level"] == "demonstrated"   # via K-Means
    assert ev["python"]["level"] == "demonstrated"             # via pandas
    assert "k-means" in ev["machine learning"]["implied_by"]


def test_implication_does_not_invent_unstated_skills():
    from src.resume_parser import parse_resume
    text = "SKILLS\nSQL\nPROJECTS\nTool\n• Used pandas.\n"
    ev = parse_resume(text)["evidence"]
    assert "python" not in ev            # implied evidence only upgrades, never adds
    assert ev["sql"]["level"] == "listed"
