# Phase 3 — Explainability & Resume Intelligence

Phase 3 turns the Phase 2 matcher into a more complete analysis product.

## Added capabilities

### 1. Evidence snippets
For every directly matched skill, CareerMatch AI attempts to show the resume line/sentence where that skill appears. This makes the score inspectable instead of presenting only a number.

### 2. Related-skill reasoning
Related matches show the resume skills that produced partial credit, e.g. a broader ML concept inferred from a configured library relation.

### 3. Project relevance ranking
Projects that overlap with job skills are ranked using:

- 65% weighted job-skill overlap
- 35% semantic similarity between the project text and JD text

The ranking is deliberately restricted to projects with detected job-skill overlap so unrelated projects do not dominate the list.

### 4. Resume improvement plan
The plan prioritises:

- High: missing required skills
- Medium: related skills that could be named explicitly if genuinely used
- Low: skills detected only in a skills list/side mention

The wording explicitly avoids telling a candidate to claim a skill they do not have.

### 5. Resume quality checks
The app checks for conventional section headings, project/experience evidence, extractable contact details and bullet-based evidence. These are structural heuristics, not guarantees about a particular ATS.

### 6. Configurable scoring
The Streamlit sidebar lets the user choose the semantic-vs-skill weighting. The two weights always sum to 100% in the UI.

### 7. Export
The dashboard can export:

- a human-readable Markdown report
- the structured JSON result

## Testing

Phase 3 adds unit tests for evidence extraction, project ranking and resume quality checks. The complete test suite currently passes locally with the project environment.
