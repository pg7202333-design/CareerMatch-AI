import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.pdf_parser import extract_pdf_text
from src.pipeline import analyze
from src.report_generator import build_report
from src.phase3_insights import build_phase3_markdown

st.set_page_config(page_title="CareerMatch AI", page_icon="🎯", layout="wide")

st.title("🎯 CareerMatch AI")
st.caption("AI-assisted resume–job matching, skill-gap analysis and evidence-grounded improvement insights")

with st.sidebar:
    st.header("How it works")
    st.markdown("""
    1. Parse the resume into sections and skill evidence.
    2. Parse the job description into required and preferred skills.
    3. Match direct, related and missing skills with evidence-aware weights.
    4. Compare meaning with sentence embeddings.
    5. Rank relevant projects using skill overlap + semantic relevance.
    6. Generate explainable improvement actions without inventing experience.
    """)
    st.divider()
    st.subheader("Scoring weights")
    semantic_pct = st.slider("Semantic similarity", 0, 100, 40, 5)
    skill_pct = 100 - semantic_pct
    st.caption(f"Skill-coverage weight: **{skill_pct}%**")
    st.info("Scores are analytical signals from text, not hiring decisions.")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area(
    "Paste Job Description", height=260,
    placeholder="Paste the complete job description here...",
)
analyze_clicked = st.button("Analyze Match", type="primary", use_container_width=True)

STATUS_ICON = {"matched": "✅", "related": "🔎", "missing": "⚠️"}
EVIDENCE_TEXT = {
    "demonstrated": "shown in projects/experience",
    "listed": "in skills list only",
    "mentioned": "mentioned elsewhere",
    "unsectioned": "found in resume text",
}

if analyze_clicked:
    if resume_file is None:
        st.warning("Please upload a PDF resume.")
        st.stop()
    if not job_description.strip():
        st.warning("Please paste a job description.")
        st.stop()

    try:
        with st.spinner("Analyzing resume and job description..."):
            resume_text = extract_pdf_text(resume_file)
            result = analyze(
                resume_text,
                job_description,
                w_semantic=semantic_pct / 100,
                w_skill=skill_pct / 100,
            )
            report = build_report(result)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    gap = result["gap"]
    for warning in result["warnings"]:
        st.warning(warning)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Match", f"{result['overall_score']:.0f}%")
    c2.metric("Skill Coverage", f"{result['skill_score']:.0f}%")
    c3.metric("Semantic Match", f"{result['semantic_score']:.0f}%")
    req = gap["required_coverage"]
    c4.metric("Required Coverage", f"{req:.0f}%" if req is not None else "n/a")
    st.progress(min(result["overall_score"] / 100, 1.0))
    st.caption(
        f"Score = {result['weights']['semantic']:.0%} semantic similarity + "
        f"{result['weights']['skill']:.0%} weighted skill coverage."
    )

    report_md = build_phase3_markdown(
        result, report, result["projects"], result["improvement_plan"], result["resume_quality_checks"]
    )
    st.download_button(
        "⬇️ Download analysis report (.md)", report_md,
        file_name="career_match_report.md", mime="text/markdown"
    )
    st.download_button(
        "⬇️ Download analysis data (.json)",
        json.dumps({k: v for k, v in result.items() if not k.startswith("_")}, indent=2, default=str),
        file_name="career_match_result.json", mime="application/json"
    )

    tab_overview, tab_gap, tab_evidence, tab_projects, tab_resume, tab_debug = st.tabs([
        "📊 Overview", "🧩 Skill Gap", "🔍 Evidence & Explainability",
        "🗂️ Projects", "📝 Resume Improvement", "⚙️ Details"
    ])

    with tab_overview:
        st.subheader("💡 Summary")
        st.write(report["summary"])

        chart_col, strength_col = st.columns([1, 1])
        with chart_col:
            st.subheader("Skill coverage")
            fig = go.Figure()
            colors = {"matched": "#2e9e5b", "related": "#e0a92b", "missing": "#d64545"}
            for status in ("matched", "related", "missing"):
                counts = [
                    sum(1 for i in gap["items"] if i["requirement"] == req_type and i["status"] == status)
                    for req_type in ("required", "preferred")
                ]
                fig.add_bar(name=status.capitalize(), x=["Required", "Preferred"], y=counts,
                            marker_color=colors[status])
            fig.update_layout(barmode="stack", height=320, margin=dict(t=10, b=10),
                              yaxis_title="Number of skills", legend_orientation="h")
            st.plotly_chart(fig, use_container_width=True)
        with strength_col:
            st.subheader("💪 Strengths")
            for line in report["strengths"] or ["No strengths could be derived from the detected skills."]:
                st.write(f"- {line}")
            st.subheader("🛠️ Improvement areas")
            for line in report["improvements"] or ["No gaps detected against the configured vocabulary."]:
                st.write(f"- {line}")

    with tab_gap:
        st.subheader("Skill-by-skill match")
        rows = [{
            "Skill": i["name"],
            "Requirement": i["requirement"],
            "Status": f"{STATUS_ICON[i['status']]} {i['status']}",
            "Evidence": EVIDENCE_TEXT.get(i["evidence_level"], "") if i["status"] == "matched"
                        else ", ".join(i["via"]),
            "Credit": round(i["credit"], 2),
            "Weight": round(i["weight"], 2),
        } for i in gap["items"]]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.write("No job skills detected from the configured vocabulary.")

        missing = [i for i in gap["items"] if i["status"] == "missing"]
        st.subheader("⚠️ Missing skills")
        if missing:
            cols = st.columns(3)
            for idx, item in enumerate(missing):
                with cols[idx % 3].container(border=True):
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"{item['requirement'].capitalize()} · weight {item['weight']:.2f}")
        else:
            st.write("No missing skills detected from the configured vocabulary.")

    with tab_evidence:
        st.subheader("Evidence found in the resume")
        matched_items = [i for i in gap["items"] if i["status"] == "matched"]
        if matched_items:
            for item in matched_items:
                snippets = result["evidence_snippets"].get(item["skill"], [])
                with st.expander(f"{item['name']} — {EVIDENCE_TEXT.get(item['evidence_level'], 'evidence')}"):
                    if snippets:
                        for snippet in snippets:
                            st.markdown(f"> {snippet}")
                    else:
                        st.caption("The skill was detected, but no short evidence snippet could be isolated.")
        else:
            st.write("No direct matched skills were detected.")

        related = [i for i in gap["items"] if i["status"] == "related"]
        if related:
            st.subheader("Related-skill reasoning")
            for item in related:
                st.write(f"- **{item['name']}** ← {', '.join(item['via'])}")

    with tab_projects:
        st.subheader("Most relevant projects")
        if result["projects"]:
            for idx, project in enumerate(result["projects"], 1):
                with st.container(border=True):
                    st.markdown(f"### {idx}. {project['title']}")
                    a, b, c = st.columns(3)
                    a.metric("Relevance", f"{project['score']:.0f}%")
                    b.metric("Skill overlap", f"{project['skill_overlap']:.0f}%")
                    c.metric("Semantic", f"{project['semantic_score']:.0f}%")
                    st.caption("Matched skills: " + (", ".join(project["skills"]) or "none directly detected"))
        else:
            st.write("No project entries were available for ranking.")

    with tab_resume:
        st.subheader("Actionable resume improvement plan")
        plan = result["improvement_plan"]
        if plan:
            st.dataframe(pd.DataFrame(plan), use_container_width=True, hide_index=True)
        else:
            st.success("No additional skill-focused actions were generated from the configured vocabulary.")

        st.subheader("Resume quality checks")
        st.dataframe(pd.DataFrame(result["resume_quality_checks"]), use_container_width=True, hide_index=True)
        st.caption("These are structural checks performed by CareerMatch AI; they are not a guarantee of compatibility with any specific ATS.")

    with tab_debug:
        with st.expander("Detected sections"):
            st.write("**Resume:** " + (", ".join(result["resume_sections"]) or "none detected"))
            st.write("**Job description:** " + (", ".join(result["jd_sections"]) or "none detected"))
            jd = result["_jd"]
            if jd["responsibilities"]:
                st.write("**Responsibilities:**")
                for line in jd["responsibilities"]:
                    st.write(f"- {line}")
        with st.expander("Detected resume skills"):
            st.write(", ".join(result["resume_skills"]) or "None")
        with st.expander("Detected job skills"):
            st.write(", ".join(result["job_skills"]) or "None")
        with st.expander("Extracted resume text"):
            st.text(result["_resume"]["text"][:12000])
