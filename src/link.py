import json
import pathlib
import typer
import frontmatter
from typing import Optional, List, Dict, Any
from src.config import settings
from src.embeddings.indexer import embed_text, search_index, add_to_index, reset_index
from src.storage.manifest import load_manifest, save_manifest, list_captures
from loguru import logger

app = typer.Typer(help="Auto-link wiki notes based on semantic similarity.")

WIKI_DIR = pathlib.Path("wiki")
INDEX_DIR = pathlib.Path("index")
EDGES_PATH = INDEX_DIR / "edges.jsonl"

def _get_note_content(wiki_path: pathlib.Path) -> str:
    if not wiki_path.exists():
        return ""
    post = frontmatter.load(str(wiki_path))
    return post.content

def _process_note(capture_id: str, rebuild: bool = False):
    meta = load_manifest(capture_id)
    if not meta:
        logger.error(f"Manifest for {capture_id} not found.")
        return
        
    status = meta.get("status")
    if status == "linked" and not rebuild:
        logger.info(f"Skipping already linked note {capture_id}.")
        return
        
    # We need to find the wiki note path. The classification result has the category.
    # Alternatively we can search wiki/**/*.md for this capture_id.
    classification = meta.get("classification")
    if not classification:
        logger.error(f"Capture {capture_id} is not classified.")
        return
        
    category = classification.get("para_category")
    wiki_path = WIKI_DIR / category / f"{capture_id}.md"
    
    if not wiki_path.exists():
        logger.error(f"Wiki note for {capture_id} not found at {wiki_path}.")
        return
        
    post = frontmatter.load(str(wiki_path))
    text = post.content
    title = post.metadata.get("title", capture_id)
    
    # 2. Compute embedding
    embedding = embed_text(text)
    
    # 3. Query FAISS
    neighbors = search_index(embedding, top_k=settings.FAISS_TOP_K + 1)
    
    # 4. Filter and build links
    links_to_add = []
    for neighbor in neighbors:
        if neighbor["id"] == capture_id:
            continue # Skip self
        if neighbor["score"] >= settings.LINK_SIM_THRESHOLD:
            links_to_add.append(neighbor)
            
    # 5. Write edge records
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(EDGES_PATH, "a", encoding="utf-8") as f:
        for link in links_to_add:
            edge = {
                "source": capture_id,
                "target": link["id"],
                "score": link["score"]
            }
            f.write(json.dumps(edge) + "\n")
            
    # 6. Insert [[target_id|title]] into ## Related section
    # First, let's update frontmatter links
    existing_links = post.metadata.get("links", [])
    new_link_ids = [l["id"] for l in links_to_add if l["id"] not in existing_links]
    
    if new_link_ids:
        post.metadata["links"] = existing_links + new_link_ids
        
    # Build ## Related section markdown
    related_md = "\n\n## Related\n\n"
    for link in links_to_add:
        related_md += f"- [[{link['id']}|{link['title']}]]\n"
        
    # Check if ## Related already exists
    if "## Related" in post.content:
        # Simple string replacement or just don't touch if it already exists for MVP
        pass
    else:
        if links_to_add:
            post.content += related_md
            
    # Save wiki note
    with open(wiki_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))
        
    # 8. Update FAISS index
    add_to_index(capture_id, str(wiki_path), title, text)
    
    # 9. Update meta.json
    meta["status"] = "linked"
    save_manifest(capture_id, meta)
    logger.info(f"Successfully linked {capture_id} (added {len(links_to_add)} links).")

@app.command()
def link(
    capture_id: Optional[str] = typer.Option(None, "--id", help="Specific capture ID to link"),
    rebuild: bool = typer.Option(False, "--rebuild", help="Rebuild entire index and re-link all notes")
):
    """Link wiki notes based on semantic similarity."""
    
    if rebuild:
        logger.info("Rebuilding index from scratch...")
        reset_index()
        if EDGES_PATH.exists():
            EDGES_PATH.unlink()
            
    candidates = list_captures() if not capture_id else [capture_id]
    
    # Sort candidates so the index builds incrementally if doing all
    for cid in candidates:
        _process_note(cid, rebuild=rebuild)

if __name__ == "__main__":
    app()
