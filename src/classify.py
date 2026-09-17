import json
import pathlib
from typing import Optional, List

import typer
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.storage.manifest import load_manifest, save_manifest, list_captures
from src.llm.prompts import get_classification_prompt
from src.llm.client import chat_completion
from pydantic import BaseModel, ValidationError, Field

app = typer.Typer(help="Classify raw captures using LLM and store results.")

class ClassificationResult(BaseModel):
    para_category: str = Field(..., description="One of Projects, Areas, Resources, Archives")
    tags: List[str] = Field(default_factory=list)
    summary: str
    title: str

# Simple exception for retry when LLM returns malformed JSON
class MalformedResponseError(Exception):
    pass

def _clean_json_str(raw: str) -> str:
    """Strip markdown codeblock wrappers if returned by the LLM."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def _parse_llm_response(response: str, is_new_capture: bool = True) -> ClassificationResult:
    """Parse the LLM raw string response into a validated ClassificationResult.
    Applies guardrails to ensure valid PARA categories and prevents unintended archival.
    """
    clean_str = _clean_json_str(response)
    try:
        data = json.loads(clean_str)
    except json.JSONDecodeError as exc:
        raise MalformedResponseError(f"Invalid JSON: {exc} from raw: {clean_str[:120]}") from exc

    # Normalize category
    raw_cat = str(data.get("para_category", "")).strip().capitalize()
    valid_cats = {"Projects", "Areas", "Resources", "Archives"}
    if raw_cat not in valid_cats:
        raw_cat = "Resources"

    # Smart Guardrail: New documents/notes/URLs should not be dumped into Archives
    if is_new_capture and raw_cat == "Archives":
        summary_lower = str(data.get("summary", "")).lower()
        title_lower = str(data.get("title", "")).lower()
        if not any(w in summary_lower or w in title_lower for w in ["archive", "obsolete", "deprecated", "completed project", "abandoned"]):
            # Check if it looks like an administrative / academic / official document -> Areas
            if any(w in summary_lower or w in title_lower for w in ["admit", "exam", "application", "allotment", "score", "jee", "university", "certificate", "id", "bill", "salary", "medical"]):
                raw_cat = "Areas"
            else:
                raw_cat = "Resources"

    data["para_category"] = raw_cat

    # Ensure title and summary are clean
    if not data.get("title") or str(data.get("title")).lower() == "placeholder title":
        data["title"] = "Saved Knowledge Document"
    if not data.get("summary") or "placeholder summary" in str(data.get("summary")).lower():
        data["summary"] = "Personal knowledge item stored and indexed in your second brain."

    try:
        return ClassificationResult(**data)
    except ValidationError as exc:
        raise MalformedResponseError(f"Schema validation error: {exc}") from exc

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(MalformedResponseError))
def _classify_text(text: str, context_hint: str = "General capture") -> ClassificationResult:
    """Send *text* to the LLM with context hint and return a validated ClassificationResult."""
    prompt = get_classification_prompt(text, context_hint=context_hint)
    raw_response = chat_completion(prompt, json_mode=True)
    if raw_response is None:
        # Graceful fallback deriving title and summary from text
        first_line = ""
        for line in text.splitlines():
            line_str = line.strip().lstrip("#").strip()
            if line_str and not line_str.startswith("http"):
                first_line = line_str[:60]
                break
        fallback_title = first_line or "Saved Knowledge Note"
        
        # Determine category based on context hint
        cat = "Resources"
        if any(w in context_hint.lower() or w in text.lower() for w in ["admit", "application", "allotment", "exam", "scorecard", "university"]):
            cat = "Areas"
            
        raw_response = json.dumps({
            "para_category": cat,
            "tags": ["knowledge", "reference"],
            "summary": f"Document concerning {fallback_title}.",
            "title": fallback_title
        })
    return _parse_llm_response(raw_response)

def _write_classification(capture_id: str, result: ClassificationResult) -> None:
    """Write ``classification.json`` and update the capture ``meta.json`` status.
    """
    raw_dir = pathlib.Path("raw") / capture_id
    classification_path = raw_dir / "classification.json"
    with open(classification_path, "w", encoding="utf-8") as f:
        json.dump(result.dict(), f, indent=2)
    # Update manifest status
    meta = load_manifest(capture_id)
    if not meta:
        meta = {}
    meta["status"] = "classified"
    meta["classification"] = result.dict()
    save_manifest(capture_id, meta)

@app.command()
def classify(
    capture_id: Optional[str] = typer.Option(None, "--id", help="Specific capture ID to classify"),
    all: bool = typer.Option(False, "--all", help="Classify all unclassified captures"),
    force: bool = typer.Option(False, "--force", help="Re‑classify even if already classified"),
):
    """Classify captures using the LLM.

    - ``--all`` processes every capture in ``raw/`` that does **not** have a status of ``classified``.
    - ``--id`` processes a single capture.
    - ``--force`` forces re‑classification, overwriting any existing ``classification.json`` and status.
    """
    if not capture_id and not all:
        typer.secho("Specify either --id <capture> or --all", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Determine which captures to process
    if all:
        candidates = list_captures()
    else:
        candidates = [capture_id]

    processed: List[str] = []
    for cid in candidates:
        meta = load_manifest(cid)
        if meta.get("status") == "classified" and not force:
            typer.secho(f"Skipping already classified capture {cid}", fg=typer.colors.YELLOW)
            continue
        content_path = pathlib.Path("raw") / cid / "content.txt"
        if not content_path.exists():
            typer.secho(f"Content file missing for {cid}", fg=typer.colors.RED)
            continue
        with open(content_path, "r", encoding="utf-8") as f:
            text = f.read()
        src_type = meta.get("source_type", "note")
        src_meta = meta.get("source_metadata", {})
        hint = f"Source Type: {src_type}"
        if "original_filename" in src_meta:
            hint += f", Filename: {src_meta['original_filename']}"
        elif "url" in src_meta:
            hint += f", URL: {src_meta['url']}"
        try:
            classification = _classify_text(text, context_hint=hint)
        except MalformedResponseError as e:
            typer.secho(f"Failed to classify {cid}: {e}", fg=typer.colors.RED)
            continue
        _write_classification(cid, classification)
        typer.secho(f"Classified {cid} as {classification.para_category}", fg=typer.colors.GREEN)
        processed.append(cid)

    typer.secho(f"Done. Processed {len(processed)} capture(s).", fg=typer.colors.CYAN)

if __name__ == "__main__":
    app()
