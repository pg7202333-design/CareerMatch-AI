from src.jd_parser import parse_job_description

SAMPLE = """AI/ML Intern

We are looking for a student with Python and machine learning experience.
Knowledge of NLP, embeddings, SQL and scikit-learn is preferred.
Familiarity with Docker and cloud platforms is a plus.
"""


def test_required_vs_preferred_without_headings():
    jd = parse_job_description(SAMPLE)
    assert jd["title"] == "AI/ML Intern"
    assert jd["required_skills"] == {"python", "machine learning"}
    assert {"natural language processing", "embeddings", "sql", "scikit-learn",
            "docker", "cloud computing"} <= jd["preferred_skills"]
    assert not (jd["required_skills"] & jd["preferred_skills"])


def test_sectioned_jd_extracts_responsibilities_and_qualifications():
    text = """Data Scientist
About us
We use AWS and Kubernetes internally.
Responsibilities
- Build NLP models
- Deploy models with Docker
Required Qualifications
- Strong Python and SQL
Preferred Qualifications
- Experience with PyTorch
Benefits
- Free Azure credits
"""
    jd = parse_job_description(text)
    assert jd["has_headings"]
    assert jd["responsibilities"] == ["Build NLP models", "Deploy models with Docker"]
    assert jd["required_qualifications"] == ["Strong Python and SQL"]
    assert jd["preferred_qualifications"] == ["Experience with PyTorch"]
    assert {"python", "sql", "natural language processing", "docker"} <= jd["required_skills"]
    assert jd["preferred_skills"] == {"pytorch"}
    # company/benefit sections are not requirements
    assert not ({"aws", "kubernetes", "azure"} & jd["all_skills"])


def test_skill_required_and_preferred_counts_as_required():
    jd = parse_job_description("Python is required. Python experience is a plus.")
    assert "python" in jd["required_skills"]
    assert "python" not in jd["preferred_skills"]


def test_mixed_cues_in_one_line_are_split():
    jd = parse_job_description("Python required; Docker is a plus")
    assert jd["required_skills"] == {"python"}
    assert jd["preferred_skills"] == {"docker"}
