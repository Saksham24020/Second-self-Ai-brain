import requests
from bs4 import BeautifulSoup
from pathlib import Path

def extract_note(text: str) -> str:
    """Extract and normalize text from a direct note string."""
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Note text cannot be empty.")
    return cleaned

def extract_url(url: str) -> str:
    """Fetch URL and extract readable text."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator="\n")
        # Collapse extra newlines and spaces
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        raise Exception(f"URL extraction failed: {str(e)}")

def extract_file(file_path: str) -> str:
    """Extract text from a file (e.g. PDF, txt)."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = path.suffix.lower()
    
    if ext in ['.txt', '.md']:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    elif ext == '.pdf':
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
