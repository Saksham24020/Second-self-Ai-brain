# SecondSelf — Phase-Wise Implementation Plan

> **Sources:** [Problem Statement](c:\Users\sidhi\Downloads\second self problem statement.md) · [Architecture](./architecture.md)  
> **Goal:** Build, test, and deploy a personal AI second brain — capture → classify → link → graph → ask.

---

## Overview

| Phase | Name                        | Maps to     | Badge              |
|-------|-----------------------------|-------------|--------------------|
| 0     | Project Setup               | Pre-Week 1  | —                  |
| 1     | Capture Pipeline            | Week 1      | 🏅 The Archivist   |
| 2     | Auto-Classification (PARA)  | Week 2.1    | —                  |
| 3     | Auto-Linking (Embeddings)   | Week 2.2    | 🏅 The Librarian   |
| 4     | Graph Build & Visualization | Week 3      | 🏅 The Cartographer|
| 5     | RAG Q&A + Streamlit UI      | Week 4      | —                  |
| 6     | Local Pipeline Testing      | Post-build  | —                  |
| 7     | Local UI Testing            | Post-build  | —                  |
| 8     | Deployment                  | Week 4.2    | —                  |
| 9     | Final Testing & Ship        | Final       | 🏅 The Oracle      |

### Dependency Chain

```
Phase 0 (Setup)
    ↓
Phase 1 (Capture) → raw/
    ↓
Phase 2 (Classify) → wiki/
    ↓
Phase 3 (Link) → index/edges.jsonl, faiss.index
    ↓
Phase 4 (Graph) → index/graph.json + viz
    ↓
Phase 5 (Ask + App) → app.py
    ↓
Phase 6–7 (Local Test)
    ↓
Phase 8 (Deploy) → public URL
    ↓
Phase 9 (Final Verify + README)
```

---

## Phase 0 — Project Setup

**Objective:** Scaffold the repository, install dependencies, configure environment, and initialize version control.

**Duration estimate:** 1–2 hours

### Tasks

#### 0.1 Create repository structure

```bash
mkdir -p secondself/{raw,wiki/{Projects,Areas,Resources,Archives},index,src/{parsing,storage,llm,embeddings},docs,tests}
touch secondself/src/__init__.py
```

Expected layout:

```
secondself/
├── raw/
├── wiki/
│   ├── Projects/
│   ├── Areas/
│   ├── Resources/
│   └── Archives/
├── index/
├── src/
│   ├── parsing/
│   ├── storage/
│   ├── llm/
│   └── embeddings/
├── docs/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

#### 0.2 Create `requirements.txt`

Pin core dependencies:

```
python-dotenv>=1.0.0
typer>=0.12.0
pydantic-settings>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pypdf>=4.0.0
sentence-transformers>=2.7.0
faiss-cpu>=1.8.0
groq>=0.9.0
tenacity>=8.2.0
loguru>=0.7.0
streamlit>=1.35.0
streamlit-agraph>=0.0.45
pyyaml>=6.0.0
python-frontmatter>=1.1.0
```

#### 0.3 Create configuration module

- [ ] `src/config.py` — load settings from `.env` via `pydantic-settings`
- [ ] `.env.example` — template with all config keys (see architecture §8)
- [ ] Copy `.env.example` → `.env` and fill in `LLM_API_KEY` (Groq free tier)

#### 0.4 Create shared utilities (stubs)

- [ ] `src/storage/manifest.py` — read/write capture manifests, list raw captures by status
- [ ] `src/parsing/text_extract.py` — stub functions for note/url/file extraction
- [ ] `src/llm/client.py` — Groq client wrapper with retry logic
- [ ] `src/llm/prompts.py` — prompt templates (classification, RAG)

#### 0.5 Initialize git

- [ ] `git init`
- [ ] `.gitignore`: `.env`, `__pycache__/`, `*.pyc`, `index/faiss.index`, `.venv/`, `raw/` (optional — keep private notes out of repo)
- [ ] Initial commit: scaffold + docs

#### 0.6 Set up Python environment

```bash
cd secondself
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

#### 0.7 Copy problem statement into repo

- [ ] Copy `second self problem statement.md` → `docs/problem-statement.md`

### Deliverables

- [ ] Full folder structure exists
- [ ] `requirements.txt` installs without errors
- [ ] `.env` configured with Groq API key
- [ ] Git repo initialized with first commit
- [ ] `src/config.py` loads settings successfully

### Verification

```bash
python -c "from src.config import settings; print(settings.LLM_PROVIDER)"
```

---

## Phase 1 — Capture Pipeline (The Archivist)

**Objective:** One CLI command captures any note, link, or file into `raw/` with a unique ID and timestamp.

**Duration estimate:** 3–5 hours  
**Badge:** 🏅 The Archivist

### Tasks

#### 1.1 Implement ID and timestamp generation

- [ ] Format: `cap_YYYYMMDD_HHMMSS_<uuid4_short>`
- [ ] ISO 8601 timestamp with timezone
- [ ] Utility in `src/storage/manifest.py`

#### 1.2 Implement text extraction (`src/parsing/text_extract.py`)

| Source | Function              | Logic                                      |
|--------|-----------------------|--------------------------------------------|
| Note   | `extract_note(text)`  | Return text as-is                          |
| URL    | `extract_url(url)`  | `requests` GET → `beautifulsoup4` strip    |
| File   | `extract_file(path)`| `pypdf` for PDF; plain read for `.txt/.md`|

- [ ] Handle extraction failures gracefully (save error in meta, still create capture)
- [ ] Store original file copy in `raw/<id>/original.<ext>` for file captures

#### 1.3 Implement `src/capture.py`

CLI via `typer`:

```bash
python src/capture.py --text "My idea about machine learning careers"
python src/capture.py --url "https://example.com/article"
python src/capture.py --file "./documents/resume.pdf"
```

For each capture, write:

- `raw/<id>/meta.json` — id, timestamp, source_type, source_metadata, status: "raw"
- `raw/<id>/content.txt` — extracted text
- `raw/<id>/original.*` — optional original file

- [ ] Validate exactly one of `--text`, `--url`, `--file` is provided
- [ ] Print capture ID on success
- [ ] Add `--verbose` flag for debug output

#### 1.4 Capture 10+ real items

Use your own scattered information — not test data:

- [ ] 4+ text notes (ideas, reminders, thoughts)
- [ ] 3+ URLs (articles, bookmarks, docs)
- [ ] 2+ files (PDF, markdown, or text file)

### Deliverables

- [ ] Working `capture.py` CLI
- [ ] `raw/` populated with 10+ real captures
- [ ] Each capture has unique ID + timestamp + content

### Acceptance Criteria

- [ ] `raw/` and `wiki/` folder structure exists
- [ ] One command captures a note, a link, AND a file
- [ ] Every capture has a timestamp + unique ID
- [ ] 10+ real items captured

### Verification

```bash
# List all captures
ls raw/
# Inspect one capture
cat raw/cap_*/meta.json
cat raw/cap_*/content.txt
```

---

## Phase 2 — Auto-Classification (The Sorting Hat)

**Objective:** Send raw captures to Groq/Llama 3 → get PARA category, tags, summary, title → write organized wiki notes.

**Duration estimate:** 4–6 hours

### Tasks

#### 2.1 Implement LLM classification prompt (`src/llm/prompts.py`)

```
System: You are a knowledge organizer using the PARA method.
Categories: Projects (active goals), Areas (ongoing responsibilities),
Resources (reference topics), Archives (inactive items).
Return ONLY valid JSON: {"para_category": "...", "tags": [...], "summary": "...", "title": "..."}

User: <capture text, truncated to ~4000 chars>
```

- [ ] Validate LLM response against expected JSON schema
- [ ] Retry on malformed JSON (up to 3 attempts via `tenacity`)

#### 2.2 Implement `src/classify.py`

```bash
# Classify all unclassified raw captures
python src/classify.py

# Classify a specific capture
python src/classify.py --id cap_20260804_143022_a1b2

# Re-classify everything (idempotent)
python src/classify.py --all --force
```

Pipeline per capture:

1. Read `raw/<id>/content.txt`
2. Call LLM → get classification JSON
3. Save `raw/<id>/classification.json`
4. Generate wiki note at `wiki/<para_category>/<id>.md` with YAML frontmatter
5. Update `raw/<id>/meta.json` status → "classified"

#### 2.3 Implement wiki note writer (`src/storage/wiki_writer.py`)

- [ ] Write Markdown with YAML frontmatter (id, para_category, tags, summary, created_at, source_type, raw_id)
- [ ] Include capture body as note content
- [ ] Idempotent: re-run updates same file (matched by raw_id)

#### 2.4 Run classification on all Phase 1 captures

- [ ] Classify all 10+ raw captures
- [ ] Verify notes appear in correct PARA folders
- [ ] Capture 5+ additional items and classify (target: 15+ total for Phase 3)

### Deliverables

- [ ] Working `classify.py` with batch and single-ID modes
- [ ] `classification.json` saved per capture
- [ ] Wiki notes in `wiki/Projects/`, `wiki/Areas/`, `wiki/Resources/`, `wiki/Archives/`

### Acceptance Criteria

- [ ] Any raw capture → category + tags + summary automatically
- [ ] PARA categorization working (all four categories represented or correctly assigned)

### Verification

```bash
python src/classify.py
ls wiki/*/
head -20 wiki/Resources/cap_*.md
cat raw/cap_*/classification.json
```

---

## Phase 3 — Auto-Linking (Connect the Dots)

**Objective:** Compute embeddings for each wiki note, find semantically similar notes, and auto-insert links between them.

**Duration estimate:** 5–7 hours  
**Badge:** 🏅 The Librarian

### Tasks

#### 3.1 Implement embedding module (`src/embeddings/indexer.py`)

- [ ] Load `sentence-transformers` model (default: `all-MiniLM-L6-v2`)
- [ ] `embed_text(text) → vector`
- [ ] `build_index(notes) → faiss.IndexFlatIP` (cosine similarity via normalized vectors)
- [ ] `search_index(query_vector, top_k) → [(note_id, score)]`
- [ ] Persist index to `index/faiss.index`
- [ ] Persist metadata mapping to `index/metadata.json` (id → wiki_path, title)

#### 3.2 Implement chunking strategy (optional for MVP)

- [ ] For notes < 512 tokens: embed whole note
- [ ] For longer notes: split into ~256-token chunks with overlap
- [ ] Store chunk → note_id mapping in metadata

#### 3.3 Implement `src/link.py`

```bash
# Link all unlinked wiki notes
python src/link.py

# Link a specific note
python src/link.py --id cap_20260804_143022_a1b2

# Rebuild entire index and re-link
python src/link.py --rebuild
```

Pipeline per note:

1. Read wiki note text
2. Compute embedding
3. Query FAISS for top-K neighbors (default K=5)
4. Filter: similarity score >= `LINK_SIM_THRESHOLD` (default 0.75)
5. Write edge records to `index/edges.jsonl`
6. Insert `[[target_id|title]]` links into note's `## Related` section
7. Update frontmatter `links` array
8. Update FAISS index
9. Update `raw/<id>/meta.json` status → "linked"

#### 3.4 Run linking on 15+ items

- [ ] Ensure 15+ classified wiki notes exist
- [ ] Run `python src/link.py --rebuild`
- [ ] Verify edges created in `index/edges.jsonl`
- [ ] Verify wiki notes contain `## Related` sections with links

### Deliverables

- [ ] Working embedding indexer with FAISS persistence
- [ ] Working `link.py` with auto-link insertion
- [ ] `index/edges.jsonl` populated with semantic edges
- [ ] 15+ organized, linked wiki notes

### Acceptance Criteria

- [ ] Embeddings computed per note
- [ ] Related notes auto-linked (no manual tagging)
- [ ] Runs on 15+ real items → organized `wiki/`

### Verification

```bash
python src/link.py --rebuild
wc -l index/edges.jsonl
grep -r "## Related" wiki/
python -c "
from src.embeddings.indexer import search_index, embed_text
q = embed_text('machine learning career')
print(search_index(q, top_k=5))
"
```

---

## Phase 4 — Graph Build & Visualization (The Cartographer)

**Objective:** Convert wiki notes and links into a graph JSON file and render an interactive force-directed graph.

**Duration estimate:** 5–7 hours  
**Badge:** 🏅 The Cartographer

### Tasks

#### 4.1 Implement link parser (`src/parsing/link_parser.py`)

- [ ] Parse `[[note_id|display title]]` syntax from wiki Markdown bodies
- [ ] Parse `links` array from YAML frontmatter
- [ ] Unit test with sample wiki note content

#### 4.2 Implement `src/build_graph.py`

```bash
python src/build_graph.py
python src/build_graph.py --output index/graph.json
```

Pipeline:

1. Scan all `wiki/**/*.md` files
2. Parse frontmatter → node attributes (id, title, para_category, tags, summary, wiki_path)
3. Parse `[[link]]` syntax + read `index/edges.jsonl` → edges
4. Deduplicate edges (same from/to pair)
5. Export `index/graph.json`

Node color mapping (for UI):

| Category   | Color  |
|------------|--------|
| Projects   | `#4A90D9` (blue)   |
| Areas      | `#50C878` (green)  |
| Resources  | `#F5A623` (orange) |
| Archives   | `#9B9B9B` (gray)   |

#### 4.3 Build interactive graph component

Choose one approach:

**Option A — `streamlit-agraph` (recommended for Streamlit integration):**

- [ ] Load `index/graph.json`
- [ ] Render force-directed graph with node colors by PARA category
- [ ] Hover → show title + summary tooltip
- [ ] Click → return selected node ID

**Option B — Custom HTML component with vis-network:**

- [ ] Generate HTML/JS snippet embedding vis-network
- [ ] Load graph JSON via Streamlit `components.html()`

Required interactions:

- [ ] Force-directed layout
- [ ] Hover popups with note summary
- [ ] Drag to reposition nodes
- [ ] Scroll/pinch to zoom

#### 4.4 Standalone graph test script

- [ ] `src/graph_viewer.py` — minimal Streamlit page that only renders the graph (for isolated testing before Phase 5)

```bash
streamlit run src/graph_viewer.py
```

### Deliverables

- [ ] Working `build_graph.py` exporting clean JSON
- [ ] `index/graph.json` with nodes and edges from real notes
- [ ] Interactive graph with hover, drag, zoom

### Acceptance Criteria

- [ ] Script builds nodes + edges from notes and exports clean JSON
- [ ] Interactive force-directed graph renders from that JSON
- [ ] Hover reveals note content
- [ ] Drag + zoom work
- [ ] Built from your real notes, not dummy data

### Verification

```bash
python src/build_graph.py
python -c "import json; g=json.load(open('index/graph.json')); print(f'{len(g[\"nodes\"])} nodes, {len(g[\"edges\"])} edges')"
streamlit run src/graph_viewer.py
```

---

## Phase 5 — RAG Q&A + Streamlit UI Assembly

**Objective:** Build the `ask()` function for retrieval-augmented Q&A and assemble the full Streamlit app with graph + search.

**Duration estimate:** 6–8 hours

### Tasks

#### 5.1 Implement `src/ask.py`

```python
def ask(question: str) -> dict:
    """
    Returns:
        {
            "answer": str,
            "sources": [{"id": str, "title": str, "excerpt": str, "score": float}]
        }
    """
```

Pipeline:

1. Embed the question (same model as Phase 3)
2. FAISS retrieve top-K notes/chunks (`RAG_TOP_K`, default 5)
3. Load full note content from wiki files
4. Build RAG prompt with retrieved context
5. Call Groq LLM to synthesize answer
6. Return answer + source citations

- [ ] Implement RAG prompt in `src/llm/prompts.py`
- [ ] Handle "insufficient context" gracefully
- [ ] Include note IDs in answer citations

CLI test:

```bash
python src/ask.py "What have I captured about machine learning?"
python src/ask.py "Summarize my career-related notes"
```

#### 5.2 Implement `src/app.py` — full Streamlit app

Layout:

```
┌─────────────────────────────────────────────────────┐
│  🧠 SecondSelf — Your Personal AI Second Brain      │
├──────────────────────────┬──────────────────────────┤
│                          │  🔍 Ask your brain       │
│   Interactive Graph      │  [Search box]  [Ask ▶]   │
│   (force-directed)       │                          │
│                          │  Answer:                 │
│   Hover → summary        │  <synthesized answer>    │
│   Click → full note      │                          │
│                          │  Sources:                │
│                          │  • Note Title (score)    │
└──────────────────────────┴──────────────────────────┘
```

Components:

- [ ] Graph panel (from Phase 4) — left column, ~60% width
- [ ] Ask panel — right column, ~40% width
- [ ] Click node → show full note content in sidebar or expander
- [ ] Ask → display answer + source list
- [ ] Optional: sidebar with capture stats (total notes, edges, categories)

Run locally:

```bash
streamlit run src/app.py
```

#### 5.3 Add pipeline orchestrator (optional convenience)

- [ ] `src/pipeline.py` — run full pipeline: classify → link → build_graph

```bash
python src/pipeline.py          # process all new captures end-to-end
python src/pipeline.py --full   # rebuild everything from scratch
```

#### 5.4 Test with real questions

Ask 5+ questions based on your captured notes:

- [ ] Question answerable from a single note
- [ ] Question requiring synthesis across multiple notes
- [ ] Question with no relevant notes (should say "I don't have enough information")
- [ ] Question about a specific topic/category
- [ ] Broad summary question ("What topics have I captured?")

### Deliverables

- [ ] Working `ask()` function with source citations
- [ ] Full `app.py` with graph + search in one Streamlit app
- [ ] Optional `pipeline.py` orchestrator

### Acceptance Criteria

- [ ] `ask()` returns answers synthesized from your own notes (retrieval + LLM)
- [ ] One Streamlit app contains both the graph and the search bar

### Verification

```bash
streamlit run src/app.py
# In browser: interact with graph, ask 3+ questions, verify source citations
```

---

## Phase 6 — Local Pipeline Testing

**Objective:** Verify the full backend pipeline works correctly on real data before deployment.

**Duration estimate:** 2–3 hours

### Tasks

#### 6.1 End-to-end pipeline test

Run the complete flow on fresh captures:

```bash
# 1. Capture 3 new items
python src/capture.py --text "New idea about productivity systems"
python src/capture.py --url "https://example.com/interesting-article"
python src/capture.py --file "./some-document.pdf"

# 2. Run full pipeline
python src/pipeline.py

# 3. Verify outputs
ls raw/                          # 3 new captures
ls wiki/*/                       # 3 new wiki notes in PARA folders
cat index/edges.jsonl | tail -5  # new edges
python src/build_graph.py        # graph updated
```

- [ ] New captures appear in `raw/`
- [ ] Classification assigns reasonable PARA categories
- [ ] Links created to existing related notes
- [ ] Graph JSON updated with new nodes/edges

#### 6.2 Idempotency test

- [ ] Re-run `classify.py` on already-classified captures → no duplicates
- [ ] Re-run `link.py` → no duplicate edges
- [ ] Re-run `build_graph.py` → same node/edge count

#### 6.3 Error handling test

- [ ] Capture with empty text → handled gracefully
- [ ] Capture with unreachable URL → error saved, capture still created
- [ ] Capture with unsupported file type → error message, no crash
- [ ] LLM returns malformed JSON → retry succeeds or fails gracefully

#### 6.4 Unit tests (`tests/`)

- [ ] `tests/test_link_parser.py` — wiki link syntax parsing
- [ ] `tests/test_classification_schema.py` — JSON validation
- [ ] `tests/test_capture.py` — ID generation, meta.json structure

```bash
python -m pytest tests/ -v
```

### Deliverables

- [ ] Pipeline runs end-to-end without errors
- [ ] Idempotency verified
- [ ] Error cases handled gracefully
- [ ] Unit tests passing

### Verification Checklist

- [ ] capture → classify → link → build_graph completes in one run
- [ ] No duplicate wiki notes or edges
- [ ] All pytest tests pass

---

## Phase 7 — Local UI Testing

**Objective:** Verify the Streamlit app works correctly locally before deploying.

**Duration estimate:** 2–3 hours

### Tasks

#### 7.1 Graph interaction tests

- [ ] Graph renders with all nodes visible
- [ ] Nodes colored correctly by PARA category
- [ ] Hover shows title + summary
- [ ] Click shows full note content
- [ ] Drag repositions nodes
- [ ] Zoom in/out works
- [ ] Graph handles 15+ nodes without performance issues

#### 7.2 Ask interaction tests

- [ ] Search box accepts input and returns answer
- [ ] Answer references specific notes from your knowledge base
- [ ] Sources panel lists note titles with relevance scores
- [ ] Empty question → helpful message
- [ ] Unanswerable question → "insufficient information" response
- [ ] Loading indicator shown during LLM call

#### 7.3 Integration smoke test

- [ ] Capture new note via CLI → run pipeline → refresh Streamlit → new node appears in graph
- [ ] Ask question about newly captured note → answer includes it

#### 7.4 UI polish

- [ ] Page title and header set
- [ ] Responsive layout (graph + ask panel side by side)
- [ ] Error messages displayed cleanly (LLM timeout, empty graph, etc.)
- [ ] Favicon or emoji in title

### Deliverables

- [ ] All graph interactions working
- [ ] All ask interactions working
- [ ] UI polished and error-free on local run

### Verification

```bash
streamlit run src/app.py
# Manual test checklist above
```

---

## Phase 8 — Deployment

**Objective:** Deploy the complete SecondSelf app to a public URL.

**Duration estimate:** 2–4 hours

### Tasks

#### 8.1 Prepare repo for deployment

- [ ] Ensure `requirements.txt` is complete and pinned
- [ ] Create `README.md` with setup instructions, screenshots, live URL
- [ ] Decide on data strategy:
  - **Option A (MVP):** Commit `index/graph.json` + sanitized demo wiki notes
  - **Option B:** Commit your real notes (only if comfortable with public access)
- [ ] Add `.streamlit/config.toml` if needed (theme, server settings)

#### 8.2 Push to GitHub

```bash
git add .
git commit -m "Complete SecondSelf MVP — capture, classify, link, graph, ask"
git remote add origin https://github.com/<username>/secondself.git
git push -u origin main
```

- [ ] Public GitHub repo created
- [ ] Code pushed

#### 8.3 Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo
3. Set main file: `src/app.py`
4. Add secrets in dashboard:
   ```
   LLM_API_KEY = gsk_...
   LLM_PROVIDER = groq
   LLM_MODEL = llama3-8b-8192
   EMBEDDING_MODEL = all-MiniLM-L6-v2
   ```
5. Deploy

**Alternative — Hugging Face Spaces:**

1. Create new Streamlit Space
2. Push repo contents
3. Set secrets via Space settings

#### 8.4 Verify deployed app

- [ ] Public URL loads without errors
- [ ] Graph renders with nodes and edges
- [ ] Ask search returns answers
- [ ] No API keys exposed in frontend

### Deliverables

- [ ] Public GitHub repo
- [ ] Live deployed URL
- [ ] Secrets configured securely

### Acceptance Criteria

- [ ] Deployed live with a public URL
- [ ] Full pipeline works end-to-end in the deployed app

---

## Phase 9 — Final Testing & Ship (The Oracle)

**Objective:** Final end-to-end verification, documentation, and project completion.

**Duration estimate:** 2–3 hours  
**Badge:** 🏅 The Oracle

### Tasks

#### 9.1 Full end-to-end verification (deployed)

Test the complete flow on the live deployment:

1. [ ] Open public URL → app loads
2. [ ] Graph displays your knowledge nodes
3. [ ] Hover/click/drag/zoom all work
4. [ ] Ask a question → get synthesized answer with sources
5. [ ] Ask unanswerable question → graceful response

#### 9.2 Full end-to-end verification (local CLI → deployed UI)

1. [ ] Capture new item locally: `python src/capture.py --text "Final test note"`
2. [ ] Run pipeline: `python src/pipeline.py`
3. [ ] Rebuild graph: `python src/build_graph.py`
4. [ ] Commit and push updated `index/graph.json`
5. [ ] Verify new node appears in deployed graph
6. [ ] Ask about the new note in deployed app

#### 9.3 Finalize README

- [ ] Project description and motivation
- [ ] Architecture overview (link to `docs/architecture.md`)
- [ ] Setup instructions (clone, venv, `.env`, install)
- [ ] Usage guide (capture, classify, link, graph, ask commands)
- [ ] Live demo URL
- [ ] Screenshots of graph and ask interface
- [ ] Tech stack summary
- [ ] License

#### 9.4 Final deliverables audit

- [ ] Public GitHub repo with clean README + setup instructions
- [ ] Live deployed URL — interactive graph + ask-your-brain search, both working
- [ ] End-to-end flow verified: capture → classify → link → graph → ask
- [ ] All 4 weekly milestones complete:
  - [ ] Week 1: Capture Pipeline (The Archivist) ✅
  - [ ] Week 2: Self-Organizing Wiki (The Librarian) ✅
  - [ ] Week 3: Living Brain (The Cartographer) ✅
  - [ ] Week 4: SecondSelf Deployment (The Oracle) ✅

### Deliverables

- [ ] All acceptance criteria met across all phases
- [ ] README complete with live URL
- [ ] Project shipped 🚀

---

## Appendix A — Command Reference

| Action                | Command                                              |
|-----------------------|------------------------------------------------------|
| Capture a note        | `python src/capture.py --text "..."`                 |
| Capture a URL         | `python src/capture.py --url "https://..."`          |
| Capture a file        | `python src/capture.py --file "./path/to/file.pdf"`  |
| Classify all          | `python src/classify.py`                             |
| Classify one          | `python src/classify.py --id cap_...`                |
| Link all              | `python src/link.py`                                 |
| Rebuild links         | `python src/link.py --rebuild`                       |
| Build graph           | `python src/build_graph.py`                          |
| Ask a question        | `python src/ask.py "Your question here"`             |
| Full pipeline         | `python src/pipeline.py`                             |
| Run app locally       | `streamlit run src/app.py`                           |
| Run graph only        | `streamlit run src/graph_viewer.py`                  |
| Run tests             | `python -m pytest tests/ -v`                         |

---

## Appendix B — Environment Variables

```env
# LLM
LLM_PROVIDER=groq
LLM_API_KEY=gsk_...
LLM_MODEL=llama3-8b-8192

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Linking
LINK_SIM_THRESHOLD=0.75
FAISS_TOP_K=5

# RAG
RAG_TOP_K=5
RAG_MAX_TOKENS=2048

# Graph
GRAPH_MAX_NODES=500

# Deployment
AUTH_REQUIRED=false
```

---

## Appendix C — Risk Mitigation

| Risk                          | Mitigation                                           | Phase |
|-------------------------------|------------------------------------------------------|-------|
| Groq API rate limits          | Batch classify with delays; cache classifications    | 2, 5  |
| Embedding model download slow | Download once in Phase 0 setup; document model name  | 0, 3  |
| No similar notes to link      | Lower threshold temporarily; capture more related items | 3   |
| Graph too cluttered           | `GRAPH_MAX_NODES` limit; filter by category          | 4     |
| LLM hallucination in RAG      | Strict "answer only from context" prompt; cite sources | 5    |
| Private notes on public URL   | Deploy demo dataset; or add auth                     | 8     |
| Streamlit component issues    | Test graph viewer standalone before full app         | 4, 7  |
| Large PDF extraction fails    | Graceful error; save partial text                      | 1     |

---

## Appendix D — Estimated Timeline

| Phase | Description              | Estimate    | Cumulative  |
|-------|--------------------------|-------------|-------------|
| 0     | Setup                    | 1–2 hours   | 2 hours     |
| 1     | Capture                  | 3–5 hours   | 7 hours     |
| 2     | Classification           | 4–6 hours   | 13 hours    |
| 3     | Auto-Linking             | 5–7 hours   | 20 hours    |
| 4     | Graph                    | 5–7 hours   | 27 hours    |
| 5     | RAG + UI                 | 6–8 hours   | 35 hours    |
| 6     | Pipeline Testing         | 2–3 hours   | 38 hours    |
| 7     | UI Testing               | 2–3 hours   | 41 hours    |
| 8     | Deployment               | 2–4 hours   | 45 hours    |
| 9     | Final Ship               | 2–3 hours   | 48 hours    |

**Total estimated effort:** ~40–50 hours (aligns with 4-week build at ~10–12 hours/week)
