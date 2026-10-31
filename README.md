# ResearchMind AI
### Research Intelligence & Knowledge Discovery Platform

ResearchMind AI is a local-first academic literature analysis application for organizing research PDFs, retrieving evidence, comparing studies, surfacing candidate research gaps and generating review reports.

## What it does

- Imports text-based academic PDFs and extracts document text and basic metadata.
- Splits papers into overlapping passages and stores them in SQLite.
- Retrieves relevant passages for cross-paper questions using TF-IDF.
- Optionally synthesizes a grounded answer with a local Ollama LLM; no cloud API key is required.
- Extracts likely objective, methodology, dataset, findings and limitations passages.
- Compares selected papers in a structured table.
- Surfaces corpus-relative research-gap hypotheses from recurring limitations and distinctive terms.
- Builds a paper-concept knowledge graph.
- Exports a literature review report in Markdown and Word formats.

## Important research integrity note

ResearchMind AI does **not** prove that a research gap is novel. It identifies candidate directions from the supplied corpus. A researcher must search wider scholarly databases, read the cited sources, verify claims and establish novelty independently. Extracted metadata and sections are heuristic and must be checked.

## Requirements

- Windows 10/11
- Python 3.10 or newer (64-bit recommended)
- 4 GB free disk space recommended for the environment and project files
- Internet access for the initial Python package installation

## Installation (Windows)

1. Extract the ZIP file.
2. Open the extracted `ResearchMind_AI` folder.
3. Install Python 3.10+ if it is not already installed. During installation, enable **Add Python to PATH**.
4. Double-click `setup_windows.bat`.
5. When installation finishes, double-click `run_windows.bat`.
6. Open the local URL shown in the terminal, usually `http://localhost:8501`.

### Manual installation

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt and run:

```bat
.venv\Scripts\activate.bat
```

## Optional local LLM setup (recommended for the full demonstration)

The application works without a language model. To enable grounded natural-language synthesis:

1. Install Ollama for Windows from https://ollama.com/download.
2. Open Command Prompt and run `ollama pull llama3.2:3b` (or another model supported by your machine).
3. Ensure the Ollama service is running.
4. In ResearchMind AI, open **Ask the Literature** and select **Local LLM synthesis · Ollama required**.
5. Keep the answer evidence cards open and verify each cited source passage.

The model receives only the passages retrieved from your local library. It is instructed to cite `[SOURCE n]` references and to acknowledge missing evidence. This reduces unsupported output but does not eliminate hallucinations.

## First-use workflow

1. Open **Research Library**.
2. Upload 3–5 text-based academic PDFs on the same research topic.
3. Select **Process selected papers**.
4. Open **Ask the Literature** and ask a question that can be answered from the uploaded studies.
5. Expand the evidence cards and inspect the source passages.
6. Open **Compare Papers**, select at least two papers and generate a comparison.
7. Open **Research Gaps** and inspect candidate directions and their evidence signals.
8. Open **Knowledge Graph** to explore shared concepts.
9. Open **Report Studio**, enter a topic and generate/export the report.

## Suggested demonstration dataset

Use 5–10 papers from one narrow research theme, for example:
- Explainable AI for intrusion detection
- Federated learning in healthcare
- Deep learning for plant disease detection
- Privacy-preserving machine learning
- Retrieval-augmented generation evaluation

Use papers that you have permission to access. Do not upload confidential or restricted documents.

## Project architecture

```text
ResearchMind_AI/
├── app.py
├── requirements.txt
├── setup_windows.bat
├── run_windows.bat
├── researchmind/
│   ├── ingestion.py
│   ├── storage.py
│   ├── analysis.py
│   ├── pipeline.py
│   ├── graph.py
│   └── reports.py
├── tests/
│   └── test_core.py
└── data/                  # created automatically; local SQLite database
```

## How the analysis works

### PDF ingestion
PyMuPDF extracts selectable text page by page. Text is normalized and split into overlapping passages so a relevant paragraph can be retrieved without requiring the entire paper to fit into a prompt.

### Evidence retrieval
The current baseline uses TF-IDF with unigram and bigram features and cosine similarity. It is deterministic, local and reproducible. This is a lexical retrieval baseline, not a neural embedding model. An optional Ollama model synthesizes an answer only from the retrieved evidence passages.

### Research gap discovery
The gap engine searches for recurring limitation-related language and terms that are distinctive within the current library. It labels the output as candidate research directions. This is exploratory corpus analysis, not proof of novelty.

### Knowledge graph
Paper nodes are connected to extracted concept nodes. Concept extraction uses TF-IDF terms. Relationships represent shared extracted vocabulary, not verified causal or scientific relationships.

## Testing

```powershell
pytest -q
```

## Known limitations and future work

- Scanned PDFs need OCR; the current version detects low-text PDFs and reports this.
- Author/year/title extraction is heuristic and may need manual correction.
- TF-IDF is sensitive to vocabulary overlap; a future version can add sentence-transformer embeddings and hybrid retrieval.
- The gap engine is corpus-relative and rule-based; future work can add citation-network analysis, scholarly API metadata and human-reviewed gap validation.
- Current question answering presents retrieved evidence passages rather than claiming unconstrained LLM reasoning. A controlled local LLM integration can be added as a later research extension.
- Multi-column layouts and mathematical notation may extract imperfectly.

## Academic evaluation suggestions

Evaluate the system on a curated collection of papers and report:
- PDF extraction success rate
- Precision@k for evidence retrieval, using manually labeled relevant passages
- Metadata extraction accuracy on a manually checked sample
- Agreement between automatically surfaced limitations and human annotation
- User-rated usefulness of candidate research directions

Do not claim accuracy figures until you have run and documented the experiments.

## Privacy

The core application processes PDFs locally and stores extracted text in `data/researchmind.db`. The core workflow stores and processes documents locally. If you enable Ollama, prompts and retrieved passages are sent to the local Ollama service on your own machine, not to a cloud AI provider. Treat the local database as sensitive if your papers or notes are confidential.
