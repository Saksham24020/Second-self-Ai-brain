import typer
import shutil
from pathlib import Path
from src.storage.manifest import generate_capture_id, get_iso_timestamp, ensure_dirs, save_manifest
from src.parsing.text_extract import extract_note, extract_url, extract_file
from typing import Optional

app = typer.Typer()

@app.command()
def capture(
    text: Optional[str] = typer.Option(None, "--text", help="Text note to capture"),
    url: Optional[str] = typer.Option(None, "--url", help="URL to capture"),
    file: Optional[str] = typer.Option(None, "--file", help="File to capture (.txt, .md, .pdf)"),
    verbose: bool = typer.Option(False, "--verbose", help="Print debug output")
):
    """
    Capture a note, URL, or file into the SecondSelf raw directory.
    """
    # Validate exactly one option is provided
    provided = sum(x is not None for x in [text, url, file])
    if provided != 1:
        typer.secho("Error: You must provide exactly one of --text, --url, or --file", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    ensure_dirs()
    
    cap_id = generate_capture_id()
    timestamp = get_iso_timestamp()
    
    source_type = ""
    extracted_text = ""
    error_msg = ""
    source_metadata = {}
    
    if text is not None:
        source_type = "note"
        try:
            extracted_text = extract_note(text)
        except ValueError as e:
            error_msg = str(e)
            
    elif url is not None:
        source_type = "url"
        source_metadata["url"] = url
        try:
            extracted_text = extract_url(url)
        except Exception as e:
            error_msg = str(e)
            
    elif file is not None:
        source_type = "file"
        source_metadata["original_filename"] = Path(file).name
        try:
            extracted_text = extract_file(file)
        except Exception as e:
            error_msg = str(e)

    status = "raw"
    if error_msg:
        status = "invalid"
        if verbose:
            typer.secho(f"Extraction error: {error_msg}", fg=typer.colors.YELLOW)

    # Save to disk
    raw_path = Path("raw") / cap_id
    raw_path.mkdir(parents=True, exist_ok=True)
    
    # Write content
    with open(raw_path / "content.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text if extracted_text else error_msg)
        
    # Copy original file if applicable
    if file is not None and not error_msg and Path(file).exists():
        original_ext = Path(file).suffix
        shutil.copy2(file, raw_path / f"original{original_ext}")

    # Write meta
    meta = {
        "id": cap_id,
        "timestamp": timestamp,
        "source_type": source_type,
        "source_metadata": source_metadata,
        "status": status
    }
    if error_msg:
        meta["extraction_error"] = error_msg
        
    save_manifest(cap_id, meta)
    
    if status == "invalid":
        typer.secho(f"Captured with errors: {cap_id}", fg=typer.colors.YELLOW)
    else:
        typer.secho(f"Successfully captured: {cap_id}", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
