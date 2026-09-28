"""Evaluate parsing accuracy on the hand-labelled cases.

Run from the repository root:  python -m evaluation.evaluate
Needs no model download: it measures skill extraction, section detection,
required/preferred classification and project splitting, not embeddings.
"""
from pathlib import Path

from evaluation.dataset import CASES
from src.jd_parser import parse_job_description
from src.resume_parser import parse_resume
from src.skill_ontology import display


def prf(pred, gold):
    tp, fp, fn = len(pred & gold), len(pred - gold), len(gold - pred)
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 1.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return tp, fp, fn, p, r, f


def evaluate():
    rows, errors = [], []
    tot = {"resume": [0, 0, 0], "jd": [0, 0, 0]}
    cls_ok = cls_n = sec_ok = proj_ok = 0
    for c in CASES:
        resume, jd = parse_resume(c["resume"]), parse_job_description(c["jd"])
        gold_r = set(c["resume_skills"])
        gold_j = set(c["required"]) | set(c["preferred"])
        for name, pred, gold in (("resume", resume["skills"], gold_r), ("jd", jd["all_skills"], gold_j)):
            tp, fp, fn, *_ = prf(pred, gold)
            tot[name][0] += tp; tot[name][1] += fp; tot[name][2] += fn
            for s in sorted(pred - gold):
                errors.append(f"{c['id']} [{name}] false positive: {display(s)}")
            for s in sorted(gold - pred):
                errors.append(f"{c['id']} [{name}] missed: {display(s)}")
        for s in gold_j & jd["all_skills"]:
            cls_n += 1
            want = "required" if s in c["required"] else "preferred"
            got = "required" if s in jd["required_skills"] else "preferred"
            cls_ok += want == got
            if want != got:
                errors.append(f"{c['id']} [jd] wrong class for {display(s)}: got {got}, want {want}")
        rs_ok = resume["sections"].names() == c["resume_sections"]
        js_ok = jd["sections"].names() == c["jd_sections"]
        sec_ok += rs_ok + js_ok
        if not rs_ok:
            errors.append(f"{c['id']} [resume sections] got {resume['sections'].names()}, want {c['resume_sections']}")
        if not js_ok:
            errors.append(f"{c['id']} [jd sections] got {jd['sections'].names()}, want {c['jd_sections']}")
        titles = [p["title"] for p in resume["projects"]]
        proj_ok += titles == c["projects"]
        if titles != c["projects"]:
            errors.append(f"{c['id']} [projects] got {titles}, want {c['projects']}")
        rows.append((c["id"], *prf(resume["skills"], gold_r)[3:], *prf(jd["all_skills"], gold_j)[3:]))

    def micro(t):
        tp, fp, fn = t
        p = tp / (tp + fp) if tp + fp else 1.0
        r = tp / (tp + fn) if tp + fn else 1.0
        return p, r, 2 * p * r / (p + r) if p + r else 0.0

    return rows, micro(tot["resume"]), micro(tot["jd"]), (cls_ok, cls_n), (sec_ok, 2 * len(CASES)), \
        (proj_ok, len(CASES)), errors


def render(result):
    rows, res, jd, cls, sec, proj, errors = result
    lines = ["# Evaluation results", "",
             f"{len(CASES)} hand-labelled synthetic resume/JD pairs (see `evaluation/dataset.py`).", "",
             "| Case | Resume P | Resume R | Resume F1 | JD P | JD R | JD F1 |",
             "|---|---|---|---|---|---|---|"]
    for cid, rp, rr, rf, jp, jr, jf in rows:
        lines.append(f"| {cid} | {rp:.2f} | {rr:.2f} | {rf:.2f} | {jp:.2f} | {jr:.2f} | {jf:.2f} |")
    lines += ["", "| Metric | Value |", "|---|---|",
              f"| Resume skill extraction (micro P / R / F1) | {res[0]:.2f} / {res[1]:.2f} / {res[2]:.2f} |",
              f"| JD skill extraction (micro P / R / F1) | {jd[0]:.2f} / {jd[1]:.2f} / {jd[2]:.2f} |",
              f"| Required vs preferred classification | {cls[0]}/{cls[1]} correct |",
              f"| Section detection (exact set match, resumes + JDs) | {sec[0]}/{sec[1]} |",
              f"| Project splitting (exact titles) | {proj[0]}/{proj[1]} |", "",
              "## Errors", ""]
    lines += [f"- {e}" for e in errors] or ["- none"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    out = render(evaluate())
    print(out)
    Path(__file__).with_name("RESULTS.md").write_text(out, encoding="utf-8")
