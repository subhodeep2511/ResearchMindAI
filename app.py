from __future__ import annotations
import streamlit as st
import pandas as pd
from pathlib import Path
from researchmind.storage import Library
from researchmind.pipeline import ResearchPipeline
from researchmind.reports import build_markdown_report, build_docx_report
from researchmind.graph import build_graph_figure

st.set_page_config(page_title="ResearchMind AI", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
library = Library(DATA_DIR / "researchmind.db")
pipeline = ResearchPipeline(library)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1440px; }
h1,h2,h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.18); }
.rm-kicker { color:#6C8DAA; font-size:.72rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; }
.rm-muted { color:#7C8795; font-size:.9rem; }
.rm-card { border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:18px 20px; background:rgba(128,128,128,.035); }
.rm-number { font-family:'Manrope'; font-size:1.8rem; font-weight:800; letter-spacing:-.05em; }
div[data-testid="stMetric"] { border:1px solid rgba(128,128,128,.18); border-radius:12px; padding:12px 14px; }
.stButton>button { border-radius:9px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

if "selected_papers" not in st.session_state:
    st.session_state.selected_papers = []

with st.sidebar:
    st.markdown("## ◈ ResearchMind")
    st.caption("RESEARCH INTELLIGENCE WORKSPACE")
    page = st.radio("WORKSPACE", ["Overview", "Research Library", "Ask the Literature", "Compare Papers", "Research Gaps", "Knowledge Graph", "Report Studio"], label_visibility="visible")
    st.divider()
    papers = library.list_papers()
    st.caption(f"LOCAL LIBRARY · {len(papers)} PAPER(S)")
    if papers:
        st.caption("Your documents remain in the local project database.")
    st.divider()
    st.caption("ResearchMind AI · MCA Project")
    st.caption("Evidence-led research assistance")

def heading(kicker, title, description):
    st.markdown(f'<div class="rm-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="rm-muted">{description}</p>', unsafe_allow_html=True)

def require_papers():
    current = library.list_papers()
    if not current:
        st.info("Your research library is empty. Add academic PDFs in Research Library to begin.")
        return None
    return current

if page == "Overview":
    heading("WORKSPACE / OVERVIEW", "Research, with evidence.", "A structured environment for understanding literature, comparing studies and developing research directions.")
    papers = library.list_papers()
    stats = pipeline.library_stats()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Papers indexed", stats["papers"])
    c2.metric("Extracted words", f'{stats["words"]:,}')
    c3.metric("Research topics", stats["topics"])
    c4.metric("Evidence passages", stats["chunks"])
    st.write("")
    left,right = st.columns([1.35,1])
    with left:
        st.markdown("### Start a research workflow")
        st.markdown("""
        <div class="rm-card">
        <b>01 · Build your library</b><br><span class="rm-muted">Import relevant papers in PDF format. Text is extracted and indexed locally.</span><br><br>
        <b>02 · Explore the literature</b><br><span class="rm-muted">Ask cross-paper questions and inspect the passages behind each answer.</span><br><br>
        <b>03 · Find patterns and gaps</b><br><span class="rm-muted">Compare research methods, limitations, datasets and recurring themes.</span><br><br>
        <b>04 · Produce a review</b><br><span class="rm-muted">Export a structured report with traceable paper references.</span>
        </div>""", unsafe_allow_html=True)
    with right:
        st.markdown("### Recent papers")
        if papers:
            for p in papers[:6]:
                st.markdown(f"**{p['title']}**")
                st.caption(f"{p.get('authors') or 'Author not detected'} · {p.get('year') or 'Year not detected'}")
                st.divider()
        else:
            st.markdown('<div class="rm-card"><b>No papers yet</b><p class="rm-muted">Your workspace is ready. Import your first PDF to begin.</p></div>', unsafe_allow_html=True)
    st.warning("ResearchMind produces research assistance, not authoritative scientific conclusions. Verify all claims against the original publications.")

elif page == "Research Library":
    heading("WORKSPACE / LIBRARY", "Research library", "Import, organize and inspect the academic papers used throughout your analysis.")
    uploads = st.file_uploader("Add research papers (PDF)", type=["pdf"], accept_multiple_files=True, help="Text-based PDFs work best. Scanned PDFs may require OCR before they can be analyzed.")
    if uploads and st.button("Process selected papers", type="primary"):
        progress = st.progress(0)
        status = st.empty()
        for i, upload in enumerate(uploads):
            status.write(f"Processing {upload.name} …")
            result = pipeline.ingest_pdf(upload.name, upload.getvalue())
            if result["ok"]:
                st.success(f"Indexed: {result['title']} ({result['chunks']} passages)")
            else:
                st.error(f"{upload.name}: {result['error']}")
            progress.progress((i+1)/len(uploads))
        status.write("Import complete.")
        st.rerun()
    papers = library.list_papers()
    st.markdown(f"### Indexed documents · {len(papers)}")
    if papers:
        df = pd.DataFrame([{"Title":p["title"],"Authors":p.get("authors") or "—","Year":p.get("year") or "—","Pages":p.get("pages") or "—","Words":p.get("word_count",0),"Added":p["created_at"][:10]} for p in papers])
        st.dataframe(df, use_container_width=True, hide_index=True)
        with st.expander("Inspect a paper"):
            labels = {f'{p["title"]}  ·  {p["id"][:8]}':p["id"] for p in papers}
            chosen = st.selectbox("Select paper", list(labels))
            p = library.get_paper(labels[chosen])
            st.write(f"**Abstract / opening summary**")
            st.write(p.get("abstract") or p["text"][:1800] + "…")
            st.caption(f"File: {p['filename']} · SHA-256: {p['sha256'][:20]}…")
        with st.expander("Remove a paper"):
            delete_labels = {p["title"]:p["id"] for p in papers}
            target = st.selectbox("Paper to remove", list(delete_labels))
            if st.button("Delete selected paper", type="secondary"):
                library.delete_paper(delete_labels[target])
                st.success("Paper removed from the local library.")
                st.rerun()
    else:
        st.info("No PDFs have been indexed yet.")

elif page == "Ask the Literature":
    heading("WORKSPACE / QUESTION ANSWERING", "Ask the literature", "Ask a question across your indexed papers. Each response is grounded in retrieved passages.")
    papers = require_papers()
    if papers:
        question = st.text_area("Research question", placeholder="What limitations do the studies identify in current intrusion detection approaches?", height=100)
        scope = st.multiselect("Limit analysis to selected papers (optional)", [p["title"] for p in papers])
        answer_mode = st.radio("Answer mode", ["Evidence compilation · no model required", "Local LLM synthesis · Ollama required"], horizontal=True)
        model = "llama3.2:3b"
        if answer_mode.startswith("Local"):
            model = st.text_input("Ollama model name", "llama3.2:3b", help="Use a model already downloaded in Ollama, for example llama3.2:3b or qwen2.5:3b.")
        if st.button("Retrieve evidence and answer", type="primary", disabled=not question.strip()):
            selected_ids = [p["id"] for p in papers if not scope or p["title"] in scope]
            try:
                result = pipeline.answer_question(question, selected_ids, use_local_llm=answer_mode.startswith("Local"), model=model)
            except Exception as exc:
                st.error(str(exc))
                result = None
            if result is None:
                st.stop()
            st.markdown("### Evidence-led response")
            st.write(result["answer"])
            st.caption(f"Retrieval method: {result['method']} · {len(result['evidence'])} evidence passages")
            st.markdown("### Supporting passages")
            for i,e in enumerate(result["evidence"],1):
                with st.expander(f"[{i}] {e['title']} · relevance {e['score']:.3f}"):
                    st.write(e["text"])
                    st.caption(f"Paper ID: {e['paper_id']} · Page: {e.get('page') or 'Not available'}")
            st.caption("The response is a synthesis of retrieved text, not a substitute for reading the cited papers.")

elif page == "Compare Papers":
    heading("WORKSPACE / COMPARATIVE ANALYSIS", "Compare studies", "Build a structured comparison of research objectives, methods, datasets, findings and stated limitations.")
    papers = require_papers()
    if papers:
        titles = {p["title"]:p["id"] for p in papers}
        chosen = st.multiselect("Select 2–8 papers", list(titles), max_selections=8)
        if len(chosen) >= 2 and st.button("Generate comparison", type="primary"):
            result = pipeline.compare_papers([titles[t] for t in chosen])
            st.dataframe(pd.DataFrame(result["rows"]), use_container_width=True, hide_index=True)
            st.markdown("### Cross-paper observations")
            for item in result["observations"]:
                st.markdown(f"- {item}")
            st.caption("Fields are extracted heuristically from paper text. Confirm details in the original publications.")
        elif len(chosen) == 1:
            st.info("Select at least one more paper to compare.")

elif page == "Research Gaps":
    heading("WORKSPACE / DISCOVERY", "Potential research gaps", "Identify recurring limitations, underexplored themes and opportunities that emerge from your selected literature.")
    papers = require_papers()
    if papers:
        if st.button("Analyze research gaps", type="primary"):
            result = pipeline.identify_gaps()
            st.markdown("### Candidate research directions")
            st.caption("These are hypotheses generated from the current library, not proof that a topic has never been studied.")
            for i,g in enumerate(result["gaps"],1):
                with st.container(border=True):
                    st.markdown(f"**{i:02d} · {g['title']}**")
                    st.write(g["rationale"])
                    st.caption(f"Signal: {g['signal']} · Supporting papers: {', '.join(g['papers']) or 'No direct match'}")
                    st.markdown("**Suggested validation:** Search additional databases, inspect cited work and test whether the limitation remains unresolved.")
            st.markdown("### Recurring limitations")
            if result["limitations"]:
                for x in result["limitations"]:
                    st.write(f"- {x['term']} · found in {x['count']} paper(s)")
            else:
                st.info("No recurring limitation phrases were detected. Add more papers or review the extracted text.")
            st.markdown("### Underrepresented topics")
            if result["underrepresented"]:
                st.write(", ".join(result["underrepresented"]))
            st.caption("Gap detection is corpus-relative: it can only identify patterns in the documents you have supplied.")

elif page == "Knowledge Graph":
    heading("WORKSPACE / KNOWLEDGE MAP", "Research knowledge graph", "Explore relationships between papers and the concepts that appear in their text.")
    papers = require_papers()
    if papers:
        fig, stats = build_graph_figure(pipeline.graph_data())
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"{stats['nodes']} nodes · {stats['edges']} relationships · Concept links are based on shared extracted keywords.")
        else:
            st.info("Not enough shared concepts to form a graph. Add more papers with overlapping research themes.")

elif page == "Report Studio":
    heading("WORKSPACE / EXPORT", "Literature review report", "Create a structured report from your indexed collection, with transparent methodology and source references.")
    papers = require_papers()
    if papers:
        title = st.text_input("Report title", "Literature Review and Research Landscape")
        topic = st.text_input("Research area", "Enter your research topic")
        if st.button("Generate report", type="primary"):
            report = pipeline.full_report(title, topic)
            st.session_state["latest_report"] = report
            st.success("Report generated. Review the content before submission.")
        if st.session_state.get("latest_report"):
            report = st.session_state["latest_report"]
            st.markdown("### Report preview")
            st.markdown(report["markdown"])
            st.download_button("Download Markdown report", report["markdown"], file_name="researchmind_literature_review.md", mime="text/markdown")
            try:
                docx = build_docx_report(report)
                st.download_button("Download Word report", docx, file_name="researchmind_literature_review.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as exc:
                st.error(f"Word export could not be prepared: {exc}")

st.divider()
st.caption("ResearchMind AI · Local-first research workflow · Always verify generated insights against original sources.")
