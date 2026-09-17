"""build_graph.py – Phase 3: The Cartographer

Reads every wiki note (all PARA sub-folders), extracts frontmatter metadata,
and combines with semantic edges from ``index/edges.jsonl`` to produce a rich
``static/graph.json`` consumed by ``static/graph.html``.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import frontmatter  # python-frontmatter, already in requirements.txt

# ---------------------------------------------------------------------------
# Paths  (all relative to the docs/ folder = project root)
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve()        # docs/src/build_graph.py
PROJECT_ROOT = _HERE.parent.parent      # docs/
WIKI_DIR = PROJECT_ROOT / "wiki"
EDGES_PATH = PROJECT_ROOT / "index" / "edges.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "static" / "graph.json"

PARA_CATEGORIES = ["Archives", "Areas", "Projects", "Resources"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_wiki_notes(wiki_dir: Path) -> List[Dict[str, Any]]:
    """Walk every PARA sub-folder and return a list of node dicts with human-friendly titles."""
    from src.manager import derive_clean_title, derive_clean_summary
    nodes: List[Dict[str, Any]] = []
    for category in PARA_CATEGORIES:
        cat_dir = wiki_dir / category
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            try:
                post = frontmatter.load(str(md_file))
            except Exception:
                continue
            meta = post.metadata
            node_id = meta.get("id") or md_file.stem
            clean_title = derive_clean_title(node_id, meta.get("title", ""), post.content)
            clean_summary = derive_clean_summary(node_id, meta.get("summary", ""), post.content)
            tags = meta.get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",")]
            nodes.append(
                {
                    "id": node_id,
                    "label": clean_title,
                    "category": category,
                    "tags": tags,
                    "summary": clean_summary,
                }
            )
    return nodes


def _load_edges(edges_path: Path) -> List[Dict[str, Any]]:
    """Load semantic edges from ``edges.jsonl``.

    Each line: ``{"source": "cap_xxx", "target": "cap_yyy", "score": 0.87}``
    """
    edges: List[Dict[str, Any]] = []
    if not edges_path.exists():
        return edges
    with edges_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                edges.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return edges


def _build_tag_edges(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create edges between notes that share at least one tag."""
    tag_map: Dict[str, List[str]] = defaultdict(list)
    for node in nodes:
        for tag in node.get("tags", []):
            tag_map[tag].append(node["id"])

    seen: set = set()
    edges: List[Dict[str, Any]] = []
    for tag, ids in tag_map.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                key = (min(ids[i], ids[j]), max(ids[i], ids[j]))
                if key not in seen:
                    seen.add(key)
                    edges.append(
                        {
                            "source": ids[i],
                            "target": ids[j],
                            "score": 1.0,
                            "type": "tag",
                            "shared_tag": tag,
                        }
                    )
    return edges



def build_graph(wiki_dir: Path, edges_path: Path) -> Dict[str, Any]:
    """Assemble the full graph: nodes from wiki notes, edges from semantic links + shared tags."""
    nodes = _load_wiki_notes(wiki_dir)
    node_ids = {n["id"] for n in nodes}

    # Semantic edges (from linker)
    sem_edges = _load_edges(edges_path)
    sem_edges = [
        e for e in sem_edges
        if e.get("source") in node_ids and e.get("target") in node_ids
    ]
    for e in sem_edges:
        e["type"] = "semantic"

    # Tag-based edges
    tag_edges = _build_tag_edges(nodes)

    # Merge, dedup by (source, target) pair
    all_edges: List[Dict[str, Any]] = sem_edges[:]
    existing = {(e["source"], e["target"]) for e in all_edges}
    existing |= {(e["target"], e["source"]) for e in all_edges}
    for e in tag_edges:
        pair = (e["source"], e["target"])
        if pair not in existing and (pair[1], pair[0]) not in existing:
            all_edges.append(e)
            existing.add(pair)

    return {"nodes": nodes, "edges": all_edges}


def save_graph(graph: Dict[str, Any], path: Path) -> None:
    """Write *graph* as pretty-printed JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)


def generate_graph() -> None:
    """Entry-point used by the pipeline."""
    graph = build_graph(WIKI_DIR, EDGES_PATH)
    save_graph(graph, OUTPUT_PATH)
    print(
        f"Graph generated: {len(graph['nodes'])} nodes, "
        f"{len(graph['edges'])} edges -> {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    generate_graph()
