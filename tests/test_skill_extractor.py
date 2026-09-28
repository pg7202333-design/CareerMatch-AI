from src.skill_extractor import extract_skills, find_related_skills, related_evidence


def test_extract_common_skills():
    skills = extract_skills("Python, SQL, machine learning and scikit-learn")
    assert {"python", "sql", "machine learning", "scikit-learn"} <= skills


def test_nlp_alias_is_one_concept():
    assert extract_skills("NLP") == {"natural language processing"}
    assert extract_skills("natural language processing") == {"natural language processing"}


def test_dsa_expands_to_both_concepts_without_duplicate():
    skills = extract_skills("Strong DSA fundamentals")
    assert skills == {"data structures", "algorithms"}
    assert "dsa" not in skills


def test_c_is_not_matched_inside_c_plus_plus():
    assert "c" not in extract_skills("I know C++ well")
    assert "c" in extract_skills("Languages: C, C++")


def test_nodejs_does_not_imply_javascript():
    skills = extract_skills("Built APIs with Node.js")
    assert skills == {"node.js"}


def test_verb_react_is_not_the_library():
    assert "react" not in extract_skills("Able to react quickly to change")
    assert "react" in extract_skills("Frontend in React and Tailwind")


def test_urls_and_emails_are_ignored():
    text = "me@example.com github.com/someone https://linkedin.com/in/someone"
    assert extract_skills(text) == set()


def test_github_and_git_are_distinct():
    assert extract_skills("GitHub") == {"github"}
    assert extract_skills("Git") == {"git"}


def test_cv_is_not_computer_vision():
    assert "computer vision" not in extract_skills("Please send your CV")


def test_related_evidence_implies_and_siblings():
    assert related_evidence({"pytorch"}, "machine learning") == ["pytorch"]
    assert related_evidence({"tensorflow"}, "pytorch") == ["tensorflow"]
    assert related_evidence({"python"}, "machine learning") == []


def test_find_related_excludes_direct_matches():
    related = find_related_skills({"pytorch", "machine learning"}, {"machine learning", "deep learning"})
    assert related == {"deep learning"}
