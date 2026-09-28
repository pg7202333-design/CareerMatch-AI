"""Hand-labelled evaluation cases (synthetic resumes/JDs written for this project).

Labels record what a human reader would say is *stated* in the text, restricted to
the skills in src/skill_ontology.py. They were written from the text, not from the
extractor's output. Cases 3 and 4 deliberately include things the rule-based
extractor is expected to get wrong.
"""

JD_ML = """Machine Learning Engineer Intern
About us
Acme AI builds tools on AWS.
Responsibilities
- Build and evaluate NLP models
- Deploy services with Docker
Required Qualifications
- Strong Python and SQL
- Experience with scikit-learn or PyTorch
Preferred Qualifications
- Knowledge of Kubernetes
- Familiarity with cloud platforms
Benefits
- Learning budget
"""

CASES = [
    {
        "id": "structured_ml_resume",
        "resume": """Aarav Mehta
aarav@example.com | github.com/aarav-example

EDUCATION
B.Tech in Computer Science, Example Institute of Technology, 2026

TECHNICAL SKILLS
Languages: Python, C++, SQL
Libraries: scikit-learn, PyTorch
Concepts: NLP, Embeddings
Tools: Git, Docker, Linux

PROJECTS
Resume Screening Tool
• Built an NLP pipeline using sentence embeddings and cosine similarity to rank resumes.
• Deployed a Streamlit app with Docker.

Crop Disease Classifier
• Trained a CNN in PyTorch on leaf images and evaluated it with cross-validation.

EXPERIENCE
Data Science Intern, Example Analytics
• Cleaned and preprocessed sales data with pandas and NumPy.
• Wrote SQL queries for reporting dashboards.

ACHIEVEMENTS
• Solved 300+ problems on coding platforms covering data structures and algorithms.
""",
        "resume_skills": ["python", "c++", "sql", "scikit-learn", "pytorch",
                          "natural language processing", "embeddings", "git", "docker", "linux",
                          "streamlit", "neural networks", "model evaluation", "pandas", "numpy",
                          "data preprocessing", "data structures", "algorithms"],
        "resume_sections": ["education", "skills", "projects", "experience", "achievements"],
        "projects": ["Resume Screening Tool", "Crop Disease Classifier"],
        "jd": JD_ML,
        "required": ["machine learning", "natural language processing", "docker", "python", "sql",
                     "scikit-learn", "pytorch"],
        "preferred": ["kubernetes", "cloud computing"],
        "jd_sections": ["about", "responsibilities", "required", "preferred", "benefits"],
    },
    {
        "id": "unsectioned_web_resume",
        "resume": """Priya Nair | priya@example.com | linkedin.com/in/priya-example
Frontend developer with 2 years of experience building web apps in React and TypeScript.
Comfortable with HTML, CSS and JavaScript. Used Node.js and MongoDB for backends.
Deployed apps on AWS. Version control with Git and GitHub.
Able to react quickly to changing requirements.
""",
        "resume_skills": ["react", "typescript", "html", "css", "javascript", "node.js",
                          "mongodb", "aws", "git", "github"],
        "resume_sections": [],
        "projects": [],
        "jd": """Full Stack Developer
Requirements
- 2+ years with JavaScript, React and Node.js
- Experience with SQL databases such as PostgreSQL
Good to have
- Docker
- Experience with CI/CD pipelines
""",
        "required": ["javascript", "react", "node.js", "sql", "postgresql"],
        "preferred": ["docker", "ci/cd"],
        "jd_sections": ["required", "preferred"],
    },
    {
        "id": "implicit_ml_analyst",
        "resume": """Rohan Gupta
SUMMARY
Analyst who enjoys turning messy data into decisions.

SKILLS
Excel, Tableau, SQL, Python (pandas, matplotlib), statistics

EXPERIENCE
Business Analyst, Example Corp
• Built dashboards for the sales team and automated weekly reports with Python.
• Trained a model to predict churn using scikit-learn and tuned it by grid search.
• Presented findings to leadership.

EDUCATION
BBA, Example College
""",
        "resume_skills": ["python", "sql", "pandas", "matplotlib", "statistics",
                          "scikit-learn", "machine learning"],
        "resume_sections": ["summary", "skills", "experience", "education"],
        "projects": [],
        "jd": """Data Analyst
What you'll do
Analyse business data and build reports in Python and SQL.
What we're looking for
Solid statistics knowledge. Experience with machine learning is helpful.
""",
        "required": ["python", "sql", "statistics"],
        "preferred": ["machine learning"],
        "jd_sections": ["responsibilities", "required"],
    },
    {
        "id": "unrelated_marketing_resume",
        "resume": """Neha Kapoor
PROFILE
Marketing graduate with experience in social media campaigns.

EXPERIENCE
Marketing Intern, Example Media
• Managed an Instagram content calendar and campaign analytics.
• Wrote copy and coordinated with designers.

SKILLS
Copywriting, Canva, Google Analytics
""",
        "resume_skills": [],
        "resume_sections": ["summary", "experience", "skills"],
        "projects": [],
        "jd": JD_ML,
        "required": ["machine learning", "natural language processing", "docker", "python", "sql",
                     "scikit-learn", "pytorch"],
        "preferred": ["kubernetes", "cloud computing"],
        "jd_sections": ["about", "responsibilities", "required", "preferred", "benefits"],
    },
    {
        "id": "pdf_style_bullets",
        "resume": """Karan Shah
TECHNICAL SKILLS
Languages: Java, Python
Frameworks: Django, Flask
PROJECTS
Library Management System
•
Designed a database with MySQL and built the backend in Java using OOP principles.
•
Wrote unit tests and set up CI/CD with GitHub Actions.
Chat Assistant
•
Built a chatbot using LLMs and prompt engineering, served through FastAPI.
EDUCATION
B.E. Computer Engineering, Example College
""",
        "resume_skills": ["java", "python", "django", "flask", "mysql",
                          "object-oriented programming", "ci/cd", "github", "llms",
                          "prompt engineering", "fastapi"],
        "resume_sections": ["skills", "projects", "education"],
        "projects": ["Library Management System", "Chat Assistant"],
        "jd": """Backend Developer
Responsibilities
- Build REST APIs using Django or FastAPI
Requirements
- Java or Python
- MySQL or PostgreSQL
Preferred
- Experience with LLMs
""",
        "required": ["rest apis", "django", "fastapi", "java", "python", "mysql", "postgresql"],
        "preferred": ["llms"],
        "jd_sections": ["responsibilities", "required", "preferred"],
    },
]
