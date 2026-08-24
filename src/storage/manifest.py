import os
import json
from datetime import datetime, timezone
import uuid
from pathlib import Path

def generate_capture_id() -> str:
    """Generate a unique ID: cap_YYYYMMDD_HHMMSS_<uuid4_short>"""
    dt_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"cap_{dt_str}_{short_uuid}"

def get_iso_timestamp() -> str:
    """Return current timestamp in ISO 8601 with timezone."""
    return datetime.now(timezone.utc).isoformat()

def ensure_dirs():
    """Ensure all required directories exist."""
    base_dir = Path(os.getcwd()) # Use current working directory as base
    dirs_to_create = [
        base_dir / "raw",
        base_dir / "wiki" / "Projects",
        base_dir / "wiki" / "Areas",
        base_dir / "wiki" / "Resources",
        base_dir / "wiki" / "Archives",
        base_dir / "index",
        base_dir / "tests",
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

def load_manifest(capture_id: str) -> dict:
    """Load metadata manifest for a specific capture_id."""
    manifest_path = Path(f"raw/{capture_id}/meta.json")
    if not manifest_path.exists():
        return {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manifest(capture_id: str, meta: dict) -> None:
    """Save metadata manifest for a specific capture_id."""
    manifest_path = Path(f"raw/{capture_id}/meta.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def list_captures(status: str = None) -> list:
    """List capture IDs, optionally filtered by status."""
    captures = []
    raw_dir = Path("raw")
    if not raw_dir.exists():
        return captures
    for p in raw_dir.iterdir():
        if p.is_dir():
            cap_id = p.name
            if status:
                meta = load_manifest(cap_id)
                if meta.get("status") == status:
                    captures.append(cap_id)
            else:
                captures.append(cap_id)
    return captures
