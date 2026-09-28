"""Skill ontology for CareerMatch AI.

Single source of truth for:
  * canonical skills and the aliases that map to them (one concept = one entry)
  * a category per skill, which drives its importance weight
  * relations between skills, used for "related" (partial-credit) matches

Alias syntax: a plain string is matched case-insensitively on word boundaries.
A string prefixed with ``cs:`` is matched case-sensitively (used for ambiguous
tokens such as the verb "react" vs. the React library, or the letter "C").
"""

# Importance of a skill by category (multiplied with required/preferred weight).
CATEGORY_WEIGHT = {
    "language": 1.0,
    "framework": 1.0,
    "ml_concept": 1.0,
    "ml_library": 0.9,
    "cs_fundamental": 0.9,
    "database": 0.8,
    "cloud": 0.8,
    "practice": 0.8,
    "data_library": 0.7,
    "tool": 0.6,
}

# canonical key -> (display name, category, aliases)
SKILLS = {
    # languages
    "python": ("Python", "language", ["python", "python3"]),
    "c": ("C", "language", ["cs:C"]),
    "c++": ("C++", "language", ["c++", "cpp"]),
    "java": ("Java", "language", ["java"]),
    "javascript": ("JavaScript", "language", ["javascript", "js"]),
    "typescript": ("TypeScript", "language", ["typescript"]),
    "sql": ("SQL", "language", ["sql"]),
    "html": ("HTML", "language", ["html", "html5"]),
    "css": ("CSS", "language", ["css", "css3"]),
    # web / app frameworks
    "react": ("React", "framework", ["cs:React", "react.js", "reactjs"]),
    "node.js": ("Node.js", "framework", ["node.js", "nodejs"]),
    "fastapi": ("FastAPI", "framework", ["fastapi"]),
    "django": ("Django", "framework", ["django"]),
    "flask": ("Flask", "framework", ["flask"]),
    "streamlit": ("Streamlit", "framework", ["streamlit"]),
    "rest apis": ("REST APIs", "practice", ["rest api", "rest apis", "restful", "restful apis"]),
    # ML / AI concepts
    "machine learning": ("Machine Learning", "ml_concept", ["machine learning", "ml"]),
    "deep learning": ("Deep Learning", "ml_concept", ["deep learning"]),
    "neural networks": ("Neural Networks", "ml_concept",
                        ["neural network", "neural networks", "cnn", "rnn", "lstm"]),
    "natural language processing": ("Natural Language Processing", "ml_concept",
                                    ["natural language processing", "nlp"]),
    "computer vision": ("Computer Vision", "ml_concept", ["computer vision"]),
    "embeddings": ("Embeddings", "ml_concept", ["embeddings", "embedding"]),
    "llms": ("LLMs", "ml_concept",
             ["llm", "llms", "large language model", "large language models"]),
    "generative ai": ("Generative AI", "ml_concept", ["generative ai", "genai"]),
    "prompt engineering": ("Prompt Engineering", "ml_concept", ["prompt engineering"]),
    "anomaly detection": ("Anomaly Detection", "ml_concept", ["anomaly detection"]),
    "random forest": ("Random Forest", "ml_concept", ["random forest"]),
    "decision trees": ("Decision Trees", "ml_concept", ["decision tree", "decision trees"]),
    "k-means": ("K-Means", "ml_concept", ["k-means", "kmeans"]),
    "tf-idf": ("TF-IDF", "ml_concept", ["tf-idf", "tfidf"]),
    "feature engineering": ("Feature Engineering", "practice", ["feature engineering"]),
    "data preprocessing": ("Data Preprocessing", "practice",
                           ["data preprocessing", "data pre-processing", "data cleaning",
                            "data preparation", "preprocessing", "preprocessed", "preprocess"]),
    "model evaluation": ("Model Evaluation", "practice",
                         ["model evaluation", "evaluation metrics", "model validation",
                          "cross-validation", "cross validation"]),
    "statistics": ("Statistics", "cs_fundamental",
                   ["statistics", "statistical analysis", "statistical modeling"]),
    # ML libraries
    "tensorflow": ("TensorFlow", "ml_library", ["tensorflow"]),
    "keras": ("Keras", "ml_library", ["keras"]),
    "pytorch": ("PyTorch", "ml_library", ["pytorch"]),
    "scikit-learn": ("Scikit-learn", "ml_library", ["scikit-learn", "sklearn", "scikit learn"]),
    "hugging face": ("Hugging Face", "ml_library", ["hugging face", "huggingface", "transformers"]),
    "opencv": ("OpenCV", "ml_library", ["opencv"]),
    "nltk": ("NLTK", "ml_library", ["nltk"]),
    "spacy": ("spaCy", "ml_library", ["spacy"]),
    # data libraries
    "pandas": ("Pandas", "data_library", ["pandas"]),
    "numpy": ("NumPy", "data_library", ["numpy"]),
    "matplotlib": ("Matplotlib", "data_library", ["matplotlib"]),
    "plotly": ("Plotly", "data_library", ["plotly"]),
    # databases
    "postgresql": ("PostgreSQL", "database", ["postgresql", "postgres"]),
    "mysql": ("MySQL", "database", ["mysql"]),
    "mongodb": ("MongoDB", "database", ["mongodb"]),
    "database management": ("Database Management", "database", ["database management", "dbms"]),
    # cloud / devops / tools
    "cloud computing": ("Cloud Computing", "cloud",
                        ["cloud computing", "cloud platform", "cloud platforms",
                         "cloud services", "cloud infrastructure"]),
    "aws": ("AWS", "cloud", ["aws", "amazon web services"]),
    "azure": ("Azure", "cloud", ["azure"]),
    "gcp": ("GCP", "cloud", ["gcp", "google cloud"]),
    "docker": ("Docker", "tool", ["docker"]),
    "kubernetes": ("Kubernetes", "tool", ["kubernetes", "k8s"]),
    "ci/cd": ("CI/CD", "tool", ["ci/cd", "continuous integration"]),
    "git": ("Git", "tool", ["git"]),
    "github": ("GitHub", "tool", ["github"]),
    "linux": ("Linux", "tool", ["linux"]),
    # CS fundamentals ("DSA" is one alias of BOTH concepts, so it is never a separate skill)
    "data structures": ("Data Structures", "cs_fundamental",
                        ["data structures", "data structure", "dsa",
                         "data structures and algorithms"]),
    "algorithms": ("Algorithms", "cs_fundamental",
                   ["algorithms", "algorithm", "dsa", "data structures and algorithms"]),
    "object-oriented programming": ("Object-Oriented Programming", "cs_fundamental",
                                    ["object-oriented programming", "object oriented programming",
                                     "oops", "oop"]),
}

# Resume skill -> broader concepts it is evidence of ("PyTorch" evidences "Deep Learning").
IMPLIES = {
    "pytorch": {"deep learning", "machine learning", "neural networks"},
    "tensorflow": {"deep learning", "machine learning", "neural networks"},
    "keras": {"deep learning", "machine learning", "neural networks"},
    "neural networks": {"deep learning", "machine learning"},
    "deep learning": {"machine learning", "neural networks"},
    "scikit-learn": {"machine learning"},
    "random forest": {"machine learning"},
    "decision trees": {"machine learning"},
    "k-means": {"machine learning"},
    "anomaly detection": {"machine learning"},
    "tf-idf": {"natural language processing"},
    "embeddings": {"natural language processing"},
    "nltk": {"natural language processing"},
    "spacy": {"natural language processing"},
    "hugging face": {"natural language processing", "deep learning"},
    "llms": {"generative ai", "natural language processing"},
    "opencv": {"computer vision"},
    "postgresql": {"sql", "database management"},
    "mysql": {"sql", "database management"},
    "sql": {"database management"},
    "aws": {"cloud computing"},
    "azure": {"cloud computing"},
    "gcp": {"cloud computing"},
    "pandas": {"data preprocessing"},
    "numpy": {"data preprocessing"},
    "flask": {"rest apis"},
    "fastapi": {"rest apis"},
    "django": {"rest apis"},
    "github": {"git"},
}
# Libraries/frameworks that are used *through* Python (so using them evidences Python).
for _lib in ("pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "keras", "flask",
             "django", "fastapi", "streamlit", "matplotlib", "plotly", "nltk", "spacy",
             "hugging face"):
    IMPLIES.setdefault(_lib, set()).add("python")

# Skills that are near-substitutes for one another (relation is symmetric).
_SIBLING_GROUPS = [
    {"pytorch", "tensorflow", "keras"},
    {"aws", "azure", "gcp"},
    {"flask", "fastapi", "django"},
    {"generative ai", "llms"},
    {"data structures", "algorithms"},
    {"matplotlib", "plotly"},
    {"mysql", "postgresql"},
    {"nltk", "spacy"},
]

SIBLINGS = {}
for _group in _SIBLING_GROUPS:
    for _s in _group:
        SIBLINGS.setdefault(_s, set()).update(_group - {_s})


def display(skill: str) -> str:
    """Human-readable name for a canonical skill key."""
    return SKILLS[skill][0] if skill in SKILLS else skill


def weight(skill: str) -> float:
    """Importance weight of a skill based on its category."""
    if skill not in SKILLS:
        return 0.8
    return CATEGORY_WEIGHT.get(SKILLS[skill][1], 0.8)


def _validate() -> None:
    for key, (_, category, aliases) in SKILLS.items():
        assert category in CATEGORY_WEIGHT, f"unknown category for {key}"
        assert aliases, f"{key} has no aliases"
    for src, targets in IMPLIES.items():
        assert src in SKILLS, src
        for t in targets:
            assert t in SKILLS, t


_validate()
