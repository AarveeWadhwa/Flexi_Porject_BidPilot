
"""Extract text from TXT, Markdown, or PDF files."""
from pathlib import Path


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".text"}:
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF support requires pypdf. Run: pip install -r requirements.txt") from exc
        reader = PdfReader(str(path))
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"[Page {page_number}]\n{text}")
        return "\n\n".join(pages)

    raise ValueError(f"Unsupported file type '{suffix}'. Use TXT, MD, or PDF.")
