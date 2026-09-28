# Evaluation results

5 hand-labelled synthetic resume/JD pairs (see `evaluation/dataset.py`).

| Case | Resume P | Resume R | Resume F1 | JD P | JD R | JD F1 |
|---|---|---|---|---|---|---|
| structured_ml_resume | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| unsectioned_web_resume | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| implicit_ml_analyst | 1.00 | 0.86 | 0.92 | 1.00 | 1.00 | 1.00 |
| unrelated_marketing_resume | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| pdf_style_bullets | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

| Metric | Value |
|---|---|
| Resume skill extraction (micro P / R / F1) | 1.00 / 0.98 / 0.99 |
| JD skill extraction (micro P / R / F1) | 1.00 / 1.00 / 1.00 |
| Required vs preferred classification | 37/37 correct |
| Section detection (exact set match, resumes + JDs) | 10/10 |
| Project splitting (exact titles) | 5/5 |

## Errors

- implicit_ml_analyst [resume] missed: Machine Learning
