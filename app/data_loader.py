from pathlib import Path
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Dict, List, Tuple
from slug import slug

DOC_ROOT = Path("data/hospital_docs")

def read_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def read_pdf(path: Path) -> str:
    return extract_text(str(path)) or ""

def load_raw_texts_by_dept(root: Path = DOC_ROOT) -> Dict[str, List[str]]:
    """
    Returns {dept: [doc_texts...]} for each subfolder under data/hospital_docs.
    Folders without supported files are skipped.
    """
    data: Dict[str, List[str]] = {}
    for dept_dir in sorted(root.iterdir()):
        if not dept_dir.is_dir():
            continue
        texts: List[str] = []
        for p in dept_dir.glob("*"):
            if p.suffix.lower() in {".html", ".htm"}:
                texts.append(read_html(p))
            elif p.suffix.lower() == ".pdf":
                texts.append(read_pdf(p))
            elif p.suffix.lower() in {".txt", ".md"}:
                texts.append(p.read_text(encoding="utf-8", errors="ignore"))
        if texts:
            data[slug(dept_dir.name)] = texts  #normalize folder name
    return data

def chunk_texts(texts: List[str], chunk_size=600, chunk_overlap=80) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks: List[str] = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def load_and_chunk_by_dept() -> Dict[str, List[str]]:
    raw = load_raw_texts_by_dept()
    return {dept: chunk_texts(texts) for dept, texts in raw.items()}
