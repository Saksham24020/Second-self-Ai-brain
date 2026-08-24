# SecondSelf — System Architecture

> **Project:** SecondSelf — Your Personal AI Second Brain  
> **Purpose:** End-to-end system to capture anything, auto-organize it with AI, link related knowledge, visualize it as an interactive graph, and answer questions from your own notes.

---

## 1. Executive Summary

SecondSelf is a **capture → classify → link → graph → ask** pipeline exposed through a **Streamlit web app** deployed at a public URL. It is not a traditional notes app or chatbot — it is a self-organizing knowledge system that compounds what you capture over time.

### End-to-End Flow

```
Capture (note / link / file)
        ↓
AI classifies & files (PARA method)
        ↓
AI auto-links related notes (embeddings)
        ↓
Interactive knowledge graph (force-directed)
        ↓
Natural-language Q&A (RAG over your notes)
        ↓
Public deployment (Streamlit Cloud / HF Spaces)
```

### Four Weekly Milestones

| Week | Codename     | Deliverable                          |
|------|--------------|--------------------------------------|
| 1    | The Archivist  | Capture pipeline → `raw/`            |
| 2    | The Librarian  | PARA classify + auto-link → `wiki/`  |
| 3    | The Cartographer | Graph JSON + interactive viz       |
| 4    | The Oracle     | RAG Q&A + Streamlit app + deploy     |

---

## 2. Design Principles

1. **Lossless ingestion** — Every capture lands in `raw/` with a unique ID and timestamp. Nothing is discarded.
2. **Deterministic derivations** — `wiki/`, embeddings, and `graph.json` are rebuildable outputs from `raw/`.
3. **Separation of concerns** — Each pipeline stage is an independent script/module with clear inputs and outputs.
4. **Idempotency** — Re-running classify/link/graph steps on the same data produces consistent results.
5. **Local-first, cloud-optional** — Filesystem storage for MVP; embeddings run locally (free); LLM calls are the only external dependency.
6. **Transparency** — Q&A answers cite which notes were used; auto-links record similarity scores.

---

## 3. Technology Stack

### Backend / Pipeline (Python)

| Component            | Choice                          | Rationale                                      |
|----------------------|---------------------------------|------------------------------------------------|
| Language             | Python 3.11+                    | Ecosystem for ML, LLM, and Streamlit           |
| CLI                  | `typer`                         | Clean one-command interface for capture        |
| Config               | `pydantic-settings`             | Typed env-based configuration                  |
| LLM (classify + ask) | Groq / Llama 3 (free tier)      | Fast, free inference for classification & RAG  |
| Embeddings           | `sentence-transformers` (local) | Free, offline-capable semantic search          |
| Vector index         | `faiss-cpu`                     | Fast similarity search over embeddings         |
| PDF extraction       | `pypdf`                         | Simple text extraction from PDFs               |
| URL extraction       | `requests` + `beautifulsoup4`   | Fetch and extract readable text from links     |
| Retries              | `tenacity`                      | Resilient LLM API calls                        |
| Logging              | `loguru` or stdlib `logging`    | Pipeline observability                         |

### Frontend / UI

| Component     | Choice                              | Rationale                                |
|---------------|-------------------------------------|------------------------------------------|
| App framework | Streamlit                           | Required by spec; single-app deployment  |
| Graph library | `vis-network` or Cytoscape.js       | Force-directed, hover, drag, zoom        |
| Graph data    | `index/graph.json`                  | Decoupled from rendering                 |

### Deployment

| Component   | Choice                          |
|-------------|---------------------------------|
| Platform    | Streamlit Cloud or HF Spaces    |
| Secrets     | Environment variables (API keys)|
| Repo        | Public GitHub repo + README     |

---

## 4. Repository Structure

```
secondself/
├── raw/                          # Week 1: append-only raw captures
│   └── <capture_id>/
│       ├── meta.json             # id, timestamp, source_type, metadata
│       ├── content.txt           # extracted/normalized text
│       └── original.*            # optional: original file copy
│
├── wiki/                         # Week 2: organized, linked notes
│   ├── Projects/
│   ├── Areas/
│   ├── Resources/
│   └── Archives/
│       └── <note_id>.md          # Markdown with YAML frontmatter
│
├── index/                        # Derived indexes (rebuildable)
│   ├── graph.json                # Week 3: nodes + edges for UI
│   ├── edges.jsonl               # Semantic link records
│   ├── faiss.index               # Embedding vector index
│   └── metadata.json             # id → wiki path, chunk mappings
│
├── src/
│   ├── capture.py                # Week 1: one-command capture
│   ├── classify.py               # Week 2.1: PARA classification
│   ├── link.py                   # Week 2.2: embeddings + auto-linking
│   ├── build_graph.py            # Week 3.1: wiki → graph.json
│   ├── ask.py                    # Week 4.1: RAG Q&A
│   ├── app.py                    # Week 4.2: Streamlit UI
│   ├── parsing/                  # Text extraction, link parsing
│   ├── storage/                  # Load/save manifests and records
│   ├── llm/                      # LLM client + prompt templates
│   └── embeddings/               # Embed + FAISS index management
│
├── docs/
│   ├── architecture.md           # This document
│   ├── implementation-plan.md    # Phase-wise build plan
│   └── edge-case.md              # Corner scenarios
│
├── requirements.txt
├── .env.example                  # Template for API keys / config
├── .gitignore
└── README.md
```

---

## 5. Data Models

### 5.1 Raw Capture Record

Each capture gets a stable ID: `cap_YYYYMMDD_HHMMSS_<uuid4_short>`.

**`raw/<id>/meta.json`**

```json
{
  "id": "cap_20260804_143022_a1b2",
  "timestamp": "2026-08-04T14:30:22+05:30",
  "source_type": "note | url | file",
  "source_metadata": {
    "url": "https://example.com",
    "title": "Example Page",
    "domain": "example.com",
    "original_filename": "paper.pdf",
    "mime_type": "application/pdf"
  },
  "status": "raw | classified | linked"
}
```

**`raw/<id>/content.txt`** — Extracted/normalized text content ready for classification.

### 5.2 Classification Output

**`raw/<id>/classification.json`**

```json
{
  "para_category": "Projects | Areas | Resources | Archives",
  "tags": ["machine-learning", "career"],
  "summary": "One-line summary of the capture.",
  "title": "Derived title for the note"
}
```

**PARA framework reference:**

| Category   | Meaning                                              |
|------------|------------------------------------------------------|
| Projects   | Active efforts with a defined outcome and deadline   |
| Areas      | Ongoing responsibilities with standards to maintain    |
| Resources  | Topics of interest for future reference              |
| Archives   | Inactive items from the other three categories       |

### 5.3 Wiki Note Format

Each classified capture becomes a Markdown file at `wiki/<para_category>/<note_id>.md`.

```markdown
---
id: cap_20260804_143022_a1b2
para_category: Resources
tags: [machine-learning, career]
summary: One-line summary of the capture.
created_at: 2026-08-04T14:30:22+05:30
source_type: url
raw_id: cap_20260804_143022_a1b2
links:
  - target_id: cap_20260803_091500_c3d4
    score: 0.87
    method: embedding
---

# Derived Title

Note body content here.

## Related
- [[cap_20260803_091500_c3d4|Related Note Title]]
```

**Link syntax:** `[[<note_id>|<display title>]]` — parsed by `build_graph.py` to create edges.

### 5.4 Semantic Edge Record

**`index/edges.jsonl`** (one JSON object per line)

```json
{"from_id": "cap_...", "to_id": "cap_...", "score": 0.87, "method": "embedding", "created_at": "2026-08-04T15:00:00+05:30"}
```

### 5.5 Graph Export

**`index/graph.json`**

```json
{
  "nodes": [
    {
      "id": "cap_20260804_143022_a1b2",
      "title": "Derived Title",
      "para_category": "Resources",
      "tags": ["machine-learning"],
      "summary": "One-line summary.",
      "wiki_path": "wiki/Resources/cap_20260804_143022_a1b2.md"
    }
  ],
  "edges": [
    {
      "from": "cap_20260804_143022_a1b2",
      "to": "cap_20260803_091500_c3d4",
      "weight": 0.87,
      "kind": "embedding"
    }
  ]
}
```

---

## 6. Pipeline Architecture

### 6.1 Week 1 — Capture Pipeline (`capture.py`)

**Purpose:** One command saves anything to `raw/` with timestamp + unique ID.

```
CLI Input                    Processing                     Output
─────────                    ──────────                     ──────
--text "..."        →   Generate ID + timestamp    →   raw/<id>/meta.json
--url "https://..." →   Fetch + extract text       →   raw/<id>/content.txt
--file path.pdf     →   Parse PDF → text           →   raw/<id>/original.pdf
```

**CLI interface:**

```bash
python src/capture.py --text "My idea about X"
python src/capture.py --url "https://example.com/article"
python src/capture.py --file "./documents/paper.pdf"
```

**Text extraction by source type:**

| Source | Extraction method                              |
|--------|------------------------------------------------|
| Note   | Direct text input                              |
| URL    | `requests` fetch → `beautifulsoup4` text strip |
| File   | `pypdf` for PDFs; plain read for `.txt/.md`    |

**Acceptance criteria:**
- [ ] `raw/` and `wiki/` folder structure exists
- [ ] One command captures note, link, AND file
- [ ] Every capture has timestamp + unique ID
- [ ] 10+ real items captured

---

### 6.2 Week 2 — Classification & Auto-Linking

#### 6.2.1 Auto-Classify (`classify.py`)

**Purpose:** Send raw captures to LLM → get PARA category, tags, summary → write wiki note.

```
raw/<id>/content.txt
        ↓
   LLM prompt (strict JSON output)
        ↓
   classification.json
        ↓
   wiki/<para_category>/<id>.md
```

**LLM prompt structure:**

```
System: You are a knowledge organizer. Classify the following capture using the PARA method.
Return ONLY valid JSON with keys: para_category, tags, summary, title.

User: <extracted text>
```

**Idempotency:** Re-running on an already-classified capture updates the wiki file in place (matched by `raw_id`).

#### 6.2.2 Auto-Link (`link.py`)

**Purpose:** Compute embeddings, find similar notes, create edges and wiki links.

```
New wiki note
        ↓
   Embed text (sentence-transformers)
        ↓
   Query FAISS index (top-K neighbors)
        ↓
   Filter: similarity >= threshold (e.g. 0.75)
        ↓
   Write edge to edges.jsonl
        ↓
   Insert [[link]] into note body
        ↓
   Update FAISS index
```

**Embedding strategy:**

| Approach          | When to use                          |
|-------------------|--------------------------------------|
| Whole-note embed  | Short notes (< 512 tokens) — simple  |
| Chunked embed     | Long notes/PDFs — better retrieval   |

For chunked: store `{chunk_id, note_id, chunk_text, embedding}` in FAISS; map chunks back to note IDs at query time.

**Acceptance criteria:**
- [ ] Any raw capture → category + tags + summary automatically
- [ ] PARA categorization working
- [ ] Embeddings computed per note
- [ ] Related notes auto-linked (no manual tagging)
- [ ] Runs on 15+ real items → organized `wiki/`

---

### 6.3 Week 3 — Graph Visualization

#### 6.3.1 Graph Builder (`build_graph.py`)

**Purpose:** Read all wiki notes + edges → export `index/graph.json`.

```
wiki/**/*.md  +  index/edges.jsonl
        ↓
   Parse frontmatter (id, title, para, tags, summary)
   Parse [[link]] syntax from body
   Merge with embedding edges
        ↓
   index/graph.json
```

#### 6.3.2 Interactive Graph (Streamlit component)

**Purpose:** Render force-directed graph with hover, drag, zoom.

**Node styling by PARA category:**

| Category   | Color suggestion |
|------------|------------------|
| Projects   | Blue             |
| Areas      | Green            |
| Resources  | Orange           |
| Archives   | Gray             |

**Interactions:**
- **Hover** → popup with title + summary
- **Click** → side panel with full note content
- **Drag** → reposition node
- **Zoom** → scroll/pinch to zoom

**Acceptance criteria:**
- [ ] Script builds nodes + edges and exports clean JSON
- [ ] Interactive force-directed graph renders from JSON
- [ ] Hover reveals note content
- [ ] Drag + zoom work
- [ ] Built from real notes, not dummy data

---

### 6.4 Week 4 — RAG Q&A & Deployment

#### 6.4.1 Ask Function (`ask.py`)

**Purpose:** Natural-language search over your knowledge base.

```
User question
        ↓
   Embed question (same model as notes)
        ↓
   FAISS retrieve top-K chunks/notes
        ↓
   Build prompt: system + retrieved context + question
        ↓
   LLM synthesize answer (cite note IDs)
        ↓
   Return { answer, sources: [{id, title, excerpt}] }
```

**RAG prompt structure:**

```
System: Answer the question using ONLY the provided notes.
If the notes don't contain enough information, say so.
Cite note IDs used in your answer.

Context:
[Note cap_xxx]: <summary + relevant text>
[Note cap_yyy]: <summary + relevant text>

Question: <user question>
```

#### 6.4.2 Streamlit App (`app.py`)

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  SecondSelf — Your Personal AI Second Brain         │
├──────────────────────────┬──────────────────────────┤
│                          │  🔍 Ask your brain       │
│   Interactive Graph      │  ┌────────────────────┐  │
│   (vis-network)          │  │ Search box         │  │
│                          │  └────────────────────┘  │
│   - Force-directed       │                          │
│   - Hover → summary      │  Answer:                 │
│   - Click → full note    │  <synthesized answer>    │
│   - Drag + zoom          │                          │
│                          │  Sources:                │
│                          │  • Note Title (id)       │
│                          │  • Note Title (id)       │
└──────────────────────────┴──────────────────────────┘
```

**Acceptance criteria:**
- [ ] `ask()` returns answers synthesized from your own notes
- [ ] One Streamlit app contains both graph and search bar
- [ ] Deployed live with a public URL
- [ ] Full pipeline works end-to-end in deployed app

---

## 7. System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERACTIONS                        │
│                                                                  │
│   CLI: capture.py          Streamlit: app.py                     │
│   (note / url / file)      (graph + ask search bar)              │
└──────────┬─────────────────────────────┬─────────────────────────┘
           │                             │
           ▼                             ▼
┌──────────────────┐          ┌──────────────────────┐
│   CAPTURE LAYER  │          │   PRESENTATION LAYER │
│                  │          │                      │
│  raw/<id>/       │          │  graph.json → vis    │
│  meta.json       │          │  ask.py → RAG answer │
│  content.txt     │          │                      │
└────────┬─────────┘          └──────────┬───────────┘
         │                                 │
         ▼                                 │
┌──────────────────┐                       │
│  ENRICH LAYER    │                       │
│                  │                       │
│  classify.py     │                       │
│  (LLM → PARA)    │                       │
│       ↓          │                       │
│  wiki/<para>/    │                       │
│  <id>.md         │                       │
│       ↓          │                       │
│  link.py         │                       │
│  (embed + FAISS) │                       │
│       ↓          │                       │
│  edges.jsonl     │                       │
└────────┬─────────┘                       │
         │                                 │
         ▼                                 │
┌──────────────────┐                       │
│  INDEX LAYER     │───────────────────────┘
│                  │
│  build_graph.py  │
│  faiss.index     │
│  graph.json      │
│  metadata.json   │
└──────────────────┘
```

---

## 8. Configuration

**`.env` / environment variables:**

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

Centralized via `pydantic-settings` in `src/config.py`.

---

## 9. Deployment Architecture

### 9.1 Streamlit Cloud / HF Spaces

```
GitHub repo (public)
        ↓
Streamlit Cloud connects to repo
        ↓
Reads requirements.txt → installs deps
        ↓
Sets secrets (LLM_API_KEY) via dashboard
        ↓
Runs app.py → public URL
```

### 9.2 Data at Deploy Time

The deployed app needs access to:
- `index/graph.json` — for graph rendering
- `index/faiss.index` + `index/metadata.json` — for Q&A retrieval
- `wiki/**/*.md` — for full note content on click / in RAG context

**Options:**
1. **Commit data to repo** — Simple for MVP/demo; not ideal for private notes
2. **Build step in CI** — Run pipeline on push, commit derived artifacts
3. **External storage** — S3/GDrive sync (future enhancement)

### 9.3 Privacy & Security

| Concern              | Mitigation                                      |
|----------------------|-------------------------------------------------|
| Personal notes public| Set `AUTH_REQUIRED=true`; add Streamlit auth    |
| API keys in repo     | Use env vars only; never commit `.env`          |
| Demo vs personal     | Deploy sanitized demo dataset for public URL    |

---

## 10. Observability & Debugging

**Logging at each pipeline stage:**

| Stage     | What to log                                    |
|-----------|------------------------------------------------|
| Capture   | ID, source_type, content length                |
| Classify  | LLM request/response metadata, PARA result     |
| Link      | Top-K matches with scores, edges created       |
| Graph     | Node/edge counts, build time                   |
| Ask       | Query, retrieved note IDs, answer length       |

**Debug mode:** `--verbose` flag on any script prints intermediate artifacts (top-10 similarity matches, full LLM prompts).

---

## 11. Testing Strategy

### Unit Tests

- Link parser recognizes `[[note_id|title]]` syntax
- Classification JSON schema validation
- Embedding index round-trip (embed → store → retrieve)

### Integration Tests

- `capture → classify → link` on 3–5 real notes
- Verify `wiki/` files created with correct PARA folders
- Verify edges appear in `edges.jsonl`

### UI Smoke Tests

- Streamlit loads `graph.json` without errors
- Hover/click works on sample nodes
- Ask returns answer with source citations

---

## 12. Build Order

1. Scaffold repo structure + `requirements.txt`
2. `capture.py` → test on 10+ real items (Week 1)
3. `classify.py` → PARA categories/tags/summary (Week 2.1)
4. `link.py` → embeddings + similarity auto-linking (Week 2.2)
5. `build_graph.py` → JSON nodes/edges (Week 3.1)
6. Graph render with vis-network/Cytoscape (Week 3.2)
7. `ask.py` → retrieval-augmented Q&A (Week 4.1)
8. `app.py` → Streamlit app combining graph + search (Week 4.2)
9. Deploy to Streamlit Cloud / HF Spaces → public URL
10. Write README, push to GitHub

---

## 13. Future Extensions

- Browser extension or hotkey capture (still lands in `raw/`)
- Incremental graph updates (avoid full rebuild)
- Search results highlight nodes/edges in graph
- OCR for scanned PDFs (`pytesseract`)
- Version history for classifications (re-classify under new prompts)
- Multi-user support with per-user knowledge bases

---

## 14. Final Deliverables Checklist

- [ ] Public GitHub repo with clean README + setup instructions
- [ ] Live deployed URL — interactive graph + ask-your-brain search
- [ ] End-to-end flow verified: capture → classify → link → graph → ask
- [ ] All 4 weekly milestones complete:
  - [ ] Week 1: Capture Pipeline (The Archivist)
  - [ ] Week 2: Self-Organizing Wiki (The Librarian)
  - [ ] Week 3: Living Brain (The Cartographer)
  - [ ] Week 4: SecondSelf Deployment (The Oracle)
