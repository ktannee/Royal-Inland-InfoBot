from pathlib import Path
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_html(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def read_pdf(path: Path) -> str:
    return extract_text(str(path)) or ""

def load_raw_texts(folder="data/hospital_docs"):
    texts = []
    for p in Path(folder).glob("*"):
        if p.suffix.lower() in {".html", ".htm"}:
            texts.append(read_html(p))
        elif p.suffix.lower() == ".pdf":
            texts.append(read_pdf(p))
        elif p.suffix.lower() in {".txt", ".md"}:
            texts.append(p.read_text(encoding="utf-8", errors="ignore"))
    return texts

def chunk_texts(texts, chunk_size=600, chunk_overlap=80):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks
