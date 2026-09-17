# Implementation Plan (aligned to external 1784implementation.md)

## Phase Overview
| Phase | Name | Badge | Primary Output |
|-------|------|-------|----------------|
| 0 | Foundation | — | Repo scaffold, deps, shared libs |
| 1 | The Archivist | 🏅 The Archivist | capture.py + 10+ items in `raw/` |
| 2 | The Librarian | 🏅 The Librarian | Classified + linked wiki/ (15+ items) |
| 3 | The Cartographer | 🏅 The Cartographer | `graph.json` + interactive graph |
| 4 | The Oracle | 🏅 The Oracle | RAG ask + Streamlit UI |

---
### Phase 0 – Foundation (Day 0)
- [x] 0.1 Initialize git repo and create folder structure (already present)
- [x] 0.2 Create `requirements.txt` (exists with needed packages)
- [x] 0.3 Create virtual environment and install dependencies (done locally)
- [x] 0.4 Create `.env.example` and `.gitignore` (present)
- [ ] 0.5 Implement `lib/models.py` — shared dataclasses (❌ not created yet)
- [ ] 0.6 Implement `lib/storage.py` — filesystem helpers (❌ not created yet)

**Status:** Core scaffold is ready; missing `lib/` utilities.

---
### Phase 1 – The Archivist (Week 1)
- [x] 1.1 Implement `capture.py` core functions (implemented, captures 16 items)
- [ ] 1.2 Implement CLI with `argparse` (partial – basic CLI works, edge‑case handling not fully vetted)
- [ ] 1.3 Handle edge cases (not fully implemented)
- [x] 1.4 Capture 10+ real items (✅ 16 real items captured in `raw/`)

**Status:** Capture pipeline functional; polishing CLI & edge‑cases pending.

---
### Phase 2 – The Librarian (Week 2)
#### 2.1 Auto‑Classify
- [x] 2.1.1 Groq API key in `.env` (✅ set)
- [ ] 2.1.2 Implement `lib/llm.py` wrapper (❌ not needed for current local classification; placeholder)
- [x] 2.1.3 Implement text extraction helpers (✅ logic lives in `src/classify.py`)
- [x] 2.1.4 Implement `classify.py` (✅ all 16 raw captures classified, wiki notes generated)
- [x] 2.1.5 Run classifier on all captures (✅ done)
- [x] 2.1.6 Spot‑check 5 notes (✅ verified manually)

#### 2.2 Auto‑Link
- [x] 2.2.1 Implement `src/embeddings/indexer.py` (✅ embedding module built, FAISS index persisted)
- [x] 2.2.2 Implement `src/link.py` (✅ linking script created and runnable)
- [x] 2.2.3 Tune similarity threshold (✅ lowered to `0.65`, edges now generated)
- [x] 2.2.4 Implement `pipeline.py` orchestrator (✅ created)
- [x] 2.2.5 Capture 5+ additional items and run full pipeline (✅ total 16 items processed, edges present)

**Status:** Classification and linking complete; `index/edges.jsonl` contains semantic edges.

---
### Phase 3 – The Cartographer (Week 3)
- [x] 3.1 Build graph data model (`build_graph.py`) – reads wiki frontmatter, loads `edges.jsonl`, generates `static/graph.json`
- [x] 3.2 Create interactive graph (`static/graph.html` with vis‑network) – dark‑mode, sidebar, search, category colours, edge‑type legend
- [x] 3.3 Wire graph generation into pipeline (`python -m src.pipeline` now runs classify → link → graph)

**Status:** Complete. `static/graph.json` has 16 nodes and 120 edges. Open `static/graph.html` via a local HTTP server to explore.

---
### Phase 4 – The Oracle (Week 4)
- [x] 4.1 Implement RAG ask engine (`ask.py`) (✅ FAISS retrieval + Groq LLM integration verified)
- [x] 4.2 Build Streamlit UI (`app.py`) (✅ Streamlit web interface with citations and dark UI)
- [ ] 4.3 Deploy to Streamlit Community Cloud (optional / deployment step)

**Status:** Complete. RAG retrieval and Streamlit app built and verified.

---
## Immediate Next Steps
1. **View the graph** – serve the `static/` folder and open `graph.html` in your browser (see command below).
2. **Proceed to Phase 4** – implement `ask.py` (RAG engine) and `app.py` (Streamlit UI).
3. Continue polishing CLI and implement missing `lib/` utilities for Phase 4.

---
*All items are now aligned with the external implementation plan you provided.*
