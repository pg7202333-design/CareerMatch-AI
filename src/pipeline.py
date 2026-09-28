"""End-to-end analysis: raw resume text + raw JD text -> result dict."""
from typing import Callable, Dict, Optional

from src.jd_parser import parse_job_description
from src.matcher import calculate_match
from src.phase3_insights import evidence_snippets, improvement_plan, resume_quality_checks
from src.resume_parser import parse_resume


def analyze(resume_text: str, jd_text: str,
            semantic_fn: Optional[Callable[[str, str], float]] = None,
            w_semantic: float = 0.4, w_skill: float = 0.6) -> Dict:
    resume = parse_resume(resume_text)
    jd = parse_job_description(jd_text)
    result = calculate_match(resume, jd, semantic_fn=semantic_fn,
                             w_semantic=w_semantic, w_skill=w_skill)
    result["_resume"] = resume
    result["_jd"] = jd
    result["evidence_snippets"] = evidence_snippets(resume_text)
    result["improvement_plan"] = improvement_plan(result)
    result["resume_quality_checks"] = resume_quality_checks(resume)
    return result
