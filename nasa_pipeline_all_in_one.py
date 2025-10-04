"""
NASA Bioscience Summarizer - Complete Pipeline
==============================================

A comprehensive AI-powered system for processing NASA bioscience publications:
- Downloads and processes 608 NASA bioscience research papers
- Extracts structured sections (Results, Conclusions, Abstract)
- Creates both extractive and abstractive summaries using state-of-the-art models
- Performs scientific entity extraction using scispaCy
- Builds semantic embeddings and FAISS index for search
- Creates topic clusters using BERTopic
- Provides interactive Streamlit dashboard for exploration

Usage:
    python nasa_pipeline_all_in_one.py --mode full --sample 3    # Quick test with 3 docs
    python nasa_pipeline_all_in_one.py --mode full               # Process all papers
    python nasa_pipeline_all_in_one.py --mode serve              # Launch dashboard
    python nasa_pipeline_all_in_one.py --mode extractive --sample 10  # Only extractive summaries

Features:
- Hybrid summarization (extractive + abstractive) for better accuracy
- Scientific entity recognition for genes, proteins, processes
- Topic modeling with BERTopic for research themes
- Semantic search with FAISS for finding related papers
- Interactive dashboard with visualizations

Author: NASA Space Apps Hackathon Team
"""

import argparse
import os
import json
import re
import math
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import requests
from tqdm import tqdm
import numpy as np

# Text extraction and processing
import fitz  # PyMuPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Scientific NLP
import spacy
from spacy import displacy

# Transformers and deep learning
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Embeddings and similarity search
from sentence_transformers import SentenceTransformer
import faiss

# Topic modeling and clustering
from bertopic import BERTopic
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import umap

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Web framework
import streamlit as st

# Logging setup
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("nasa_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
ROOT = Path.cwd()
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
PAPERS_DIR = ROOT / "papers"
TEXT_DIR = ROOT / "paper_text"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
ENT_DIR = ROOT / "entities"
EMBED_DIR = ROOT / "embeddings"
TOPICS_DIR = ROOT / "topics"
DASHBOARD_DIR = ROOT / "dashboard"
FAISS_INDEX_PATH = EMBED_DIR / "faiss.index"
DOCINFO_JSON = EMBED_DIR / "docs.json"
TOPICS_JSON = TOPICS_DIR / "topics.json"

# Model configurations
ABSTRACTIVE_MODELS = {
    "led": "allenai/led-base-16384",           # Long document summarization
    "primera": "allenai/PRIMERA",              # Multi-document summarization
    "bigbird": "google/bigbird-pegasus-large-pubmed",  # Biomedical focus
    "bart": "facebook/bart-large-cnn"          # General purpose
}

EMBEDDING_MODELS = {
    "specter": "allenai-specter",              # Scientific papers
    "scibert": "allenai/scibert_scivocab_uncased",
    "mpnet": "sentence-transformers/all-mpnet-base-v2",
    "biobert": "dmis-lab/biobert-base-cased-v1.1"
}

SCISPACY_MODELS = {
    "sm": "en_core_sci_sm",                    # Small model
    "md": "en_core_sci_md",                    # Medium model
    "lg": "en_core_sci_lg"                     # Large model
}

# Default configurations
DEFAULT_ABSTRACTIVE_MODEL = "led"
DEFAULT_EMBEDDING_MODEL = "specter"
DEFAULT_SCISPACY_MODEL = "sm"

# Processing parameters
CHUNK_TOKENS = 8000
CHUNK_OVERLAP = 200
CHUNK_SUM_MAXLEN = 180
FINAL_SUM_MAXLEN = 300
NUM_BEAMS = 4
TEMPERATURE = 0.7
MAX_ENTITIES_PER_DOC = 100
NUM_TOPICS = 20
MIN_TOPIC_SIZE = 5

# -----------------------------------------------------------------------------


def ensure_dirs():
    for d in [PAPERS_DIR, TEXT_DIR, SUM_EX_DIR, SUM_AB_DIR, ENT_DIR, EMBED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


# ----------------------- 1) Read CSV and Download PDFs if needed -----------------------
def download_papers(df: pd.DataFrame, sample_n: int = None):
    """
    Download PDFs from df['link'] if direct PDF content-type returned.
    Save into PAPERS_DIR with filename '{id}_{title}.pdf' or use supplied pdf_path.
    """
    logger.info("Downloading PDFs (if link points to PDF). Set sample_n to limit how many to process.)")
    rows = df.itertuples(index=False)
    if sample_n:
        rows = list(rows)[:sample_n]
    for row in tqdm(rows):
        # try to get id/title/link/pdf_path
        rid = getattr(row, "id", None) or getattr(row, "ID", None) or None
        title = getattr(row, "title", None) or getattr(row, "Title", None) or "paper"
        link = getattr(row, "link", None) or getattr(row, "Link", None) or None
        pdf_path = getattr(row, "pdf_path", None) or None
        safe_title = re.sub(r"[^\w\d-]+", "_", str(title))[:80]
        fname = PAPERS_DIR / f"{rid or int(time.time())}_{safe_title}.pdf"
        if pdf_path and Path(pdf_path).exists():
            # copy local PDF path to PAPERS_DIR
            try:
                Path(pdf_path).replace(fname)
                logger.info("Copied local pdf %s -> %s", pdf_path, fname)
            except Exception:
                logger.warning("Could not copy %s", pdf_path)
            continue
        if link:
            try:
                r = requests.get(link, timeout=20)
                r.raise_for_status()
                ctype = r.headers.get("Content-Type", "")
                if "application/pdf" in ctype or link.lower().endswith(".pdf"):
                    fname.write_bytes(r.content)
                    logger.info("Downloaded PDF for %s", title)
                else:
                    # not a direct pdf; save HTML so you can inspect manually
                    html_fname = PAPERS_DIR / f"{rid or int(time.time())}_{safe_title}.html"
                    html_fname.write_text(r.text, encoding="utf-8")
                    logger.info("Saved HTML for %s (not direct PDF).", title)
            except Exception as e:
                logger.warning("Failed to download %s -> %s", link, e)
        else:
            logger.warning("No link/pdf_path for %s", title)


# ----------------------- 2) Extract text from PDFs (PyMuPDF) ---------------------------
def pdf_to_text(pdf_path: Path) -> str:
    """Extract raw text from PDF with PyMuPDF (works fast; two-column may be messy)."""
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.error("Could not open %s: %s", pdf_path, e)
        return ""
    pages = []
    for p in doc:
        try:
            pages.append(p.get_text("text"))
        except Exception:
            pages.append("")
    return "\n".join(pages)


def extract_sections_from_text(text: str) -> Dict[str, str]:
    """
    Naive rules-based section extraction. Looks for headings Results/Conclusion/Abstract.
    Returns dict with keys 'results', 'conclusion', 'abstract' if found.
    """
    out = {}
    # Normalize newlines
    t = text.replace("\r", "\n")
    # Try to find Results block
    r = re.search(r'(?:\n|^)(Results|RESULTS|Findings|FINDINGS|RESULT)(.*?)(?:\n(?:Conclusion|CONCLUSION|Conclusions|DISCUSSION|Discussion|METHODS|References|REFERENCES)\b)', t, re.S)
    if r:
        out['results'] = r.group(2).strip()
    # Conclusion / Discussion
    c = re.search(r'(?:\n|^)(Conclusion|CONCLUSION|Conclusions|Discussion|DISCUSSION)(.*?)(?:\n(?:References|REFERENCES|Acknowledg|ACKNOWLEDG))', t, re.S)
    if c:
        out['conclusion'] = c.group(2).strip()
    # Abstract
    a = re.search(r'(?:\n|^)(Abstract|ABSTRACT)(.*?)(?:\n(?:Introduction|INTRODUCTION|Background|BACKGROUND))', t, re.S)
    if a:
        out['abstract'] = a.group(2).strip()
    # If nothing found, create short fallback: first 1000 chars as abstract
    if not out:
        out['abstract'] = t[:2000]
    return out


def run_text_extraction(sample_n: int = None):
    """Iterate PDFs in PAPERS_DIR and create *_sections.txt files in TEXT_DIR"""
    logger.info("Extracting text from PDFs in %s", PAPERS_DIR)
    files = list(PAPERS_DIR.glob("*.pdf"))
    if sample_n:
        files = files[:sample_n]
    for f in tqdm(files):
        txt = pdf_to_text(f)
        sections = extract_sections_from_text(txt)
        # save full text and sections
        (TEXT_DIR / (f.stem + ".txt")).write_text(txt, encoding="utf-8")
        (TEXT_DIR / (f.stem + "_sections.txt")).write_text(json.dumps(sections), encoding="utf-8")


# ----------------------- 3) Extractive summarization (LexRank/TextRank) ----------------
def extractive_summarize_text(text: str, sentences_count: int = 5) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    sents = summarizer(parser.document, sentences_count)
    return " ".join([str(s) for s in sents])


def run_extractive_for_all(sample_n: int = None):
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
    for f in tqdm(files):
        sections = json.loads(f.read_text(encoding="utf-8"))
        text = sections.get('results') or sections.get('conclusion') or sections.get('abstract') or ""
        if not text.strip():
            continue
        summary = extractive_summarize_text(text, sentences_count=5)
        out_path = SUM_EX_DIR / (f.stem + "_extractive.txt")
        out_path.write_text(summary, encoding="utf-8")


# ----------------------- 4) Abstractive summarization (map-reduce chunking) ---------------
def load_abstractive_model(model_name: str = ABSTRACTIVE_MODEL):
    """Load tokenizer and model for seq2seq generation (LED/PRIMERA/BigBird)"""
    logger.info("Loading abstractive model %s ...", model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    return tokenizer, model, device


def chunk_text_for_model(text: str, tokenizer, max_tokens=CHUNK_TOKENS, overlap=CHUNK_OVERLAP) -> List[str]:
    """
    Tokenize text and produce overlapping decoded chunks that fit within max_tokens.
    Returns list of chunk strings.
    """
    toks = tokenizer(text, return_tensors="pt", truncation=False)["input_ids"][0]
    L = toks.size(0)
    chunks = []
    start = 0
    while start < L:
        end = min(start + max_tokens, L)
        chunk = tokenizer.decode(toks[start:end], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk)
        start = end - overlap
    return chunks


def summarize_chunk(c: str, tokenizer, model, device, max_len=CHUNK_SUM_MAXLEN):
    inputs = tokenizer(c, return_tensors="pt", truncation=True, max_length=tokenizer.model_max_length).to(device)
    # beam search; tune num_beams to fit memory/performance
    out = model.generate(**inputs, max_length=max_len, num_beams=NUM_BEAMS, early_stopping=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)


def run_abstractive_for_all(sample_n: int = None):
    tokenizer, model, device = load_abstractive_model()
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
    for f in tqdm(files):
        name = f.stem
        sections = json.loads(f.read_text(encoding="utf-8"))
        text = sections.get('results') or sections.get('conclusion') or sections.get('abstract') or ""
        if not text.strip():
            logger.warning("No text for %s; skipping", name)
            continue
        # chunk text
        chunks = chunk_text_for_model(text, tokenizer, max_tokens=CHUNK_TOKENS, overlap=CHUNK_OVERLAP)
        chunk_summaries = []
        for i, c in enumerate(chunks):
            try:
                cs = summarize_chunk(c, tokenizer, model, device, max_len=CHUNK_SUM_MAXLEN)
                chunk_summaries.append(cs)
            except Exception as e:
                logger.error("Chunk summarization failed for %s chunk %d: %s", name, i, e)
                # fallback: short extractive snippet
                chunk_summaries.append(c[:500])
        # reduce: summarize chunk_summaries as combined doc
        meta = "\n\n".join(chunk_summaries)
        try:
            final = summarize_chunk(meta, tokenizer, model, device, max_len=FINAL_SUM_MAXLEN)
        except Exception as e:
            logger.error("Final summarization failed for %s: %s", name, e)
            final = " ".join(chunk_summaries)[:1000]
        out = {
            "doc": name,
            "chunks": len(chunks),
            "chunk_summaries": chunk_summaries,
            "final_summary": final,
            "model": ABSTRACTIVE_MODEL
        }
        (SUM_AB_DIR / f"{name}_abstractive.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


# ----------------------- 5) scispaCy entity extraction ---------------------------------
def run_scispacy_for_all(sample_n: int = None):
    logger.info("Loading scispaCy model %s", SCISPACY_MODEL)
    nlp = spacy.load(SCISPACY_MODEL)
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
    for f in tqdm(files):
        sections = json.loads(f.read_text(encoding="utf-8"))
        text = sections.get('results') or sections.get('conclusion') or sections.get('abstract') or ""
        if not text.strip():
            continue
        doc = nlp(text)
        ents = [{"text": e.text, "label": e.label_} for e in doc.ents]
        (ENT_DIR / f"{f.stem}_entities.json").write_text(json.dumps(ents, indent=2), encoding="utf-8")


# ----------------------- 6) Embeddings + FAISS + BERTopic clustering --------------------
def compute_embeddings_and_index(sample_n: int = None):
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(EMBEDDING_MODEL)
    docs = []
    texts = []
    files = list(SUM_EX_DIR.glob("*_extractive.txt"))
    if sample_n:
        files = files[:sample_n]
    for f in files:
        text = f.read_text(encoding="utf-8")
        docs.append({"id": f.stem, "text": text})
        texts.append(text)
    if not texts:
        logger.warning("No extractive summaries to embed; run extractive step first.")
        return
    emb = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    d = emb.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(emb)
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    with open(DOCINFO_JSON, "w") as fh:
        json.dump(docs, fh)
    logger.info("Wrote FAISS index and docs.json to %s", EMBED_DIR)


def run_bertopic(sample_n: int = None):
    # Build BERTopic model on extractive summaries or abstracts
    files = list(SUM_EX_DIR.glob("*_extractive.txt"))
    if sample_n:
        files = files[:sample_n]
    texts = [f.read_text(encoding="utf-8") for f in files]
    if not texts:
        logger.warning("No texts for BERTopic; ensure extractive summaries are available.")
        return
    # Use SentenceTransformer embeddings for BERTopic
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    topic_model = BERTopic(embedding_model=embedding_model, verbose=False)
    topics, probs = topic_model.fit_transform(texts)
    # Save model and topics
    topic_model.save(EMBED_DIR / "bertopic_model")
    logger.info("BERTopic complete; top topics:\n%s", topic_model.get_topic_info().head(20).to_string())


# ----------------------- 7) Small Streamlit app to explore results ---------------------
def streamlit_app():
    st.title("NASA Bioscience Summaries - Quick Explorer")
    st.markdown("Simple demo: shows extractive + abstractive summaries, entities, and link to PDF/HTML.")
    st.sidebar.header("Options")
    docs = []
    if DOCINFO_JSON.exists():
        docs = json.loads(DOCINFO_JSON.read_text(encoding="utf-8"))
    else:
        # fallback: list files in SUM_EX_DIR
        for f in SUM_EX_DIR.glob("*_extractive.txt"):
            docs.append({"id": f.stem, "text": f.read_text(encoding="utf-8")})
    choices = {d['id']: d for d in docs}
    sel = st.sidebar.selectbox("Pick doc", list(choices.keys())[:200])
    if not sel:
        st.write("No docs found. Run pipeline first.")
        return
    entry = choices[sel]
    st.header(sel)
    st.subheader("Extractive summary")
    ex_path = SUM_EX_DIR / f"{sel}_extractive.txt"
    if ex_path.exists():
        st.write(ex_path.read_text(encoding="utf-8"))
    else:
        st.write("No extractive summary found")
    st.subheader("Abstractive summary")
    ab_path = SUM_AB_DIR / f"{sel}_abstractive.json"
    if ab_path.exists():
        s = json.loads(ab_path.read_text(encoding="utf-8"))
        st.write(s.get("final_summary",""))
        if st.button("Show chunk summaries"):
            for i, cs in enumerate(s.get("chunk_summaries",[])):
                st.write(f"Chunk {i}:", cs)
    else:
        st.write("No abstractive summary found")
    st.subheader("Entities (scispaCy)")
    ent_path = ENT_DIR / f"{sel}_entities.json"
    if ent_path.exists():
        st.write(json.loads(ent_path.read_text(encoding="utf-8")))
    else:
        st.write("No entities found")
    st.subheader("Source files")
    # find matching pdf/html
    pdfs = list(PAPERS_DIR.glob(f"{sel}*")) + list(PAPERS_DIR.glob(f"*{sel}*"))
    for p in pdfs[:10]:
        st.write("File:", p.name, " — path:", str(p))


# ----------------------- CLI and orchestration ----------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full","download","extract_text","extractive","abstractive","entities","embed","topic","serve"], default="full",
                        help="Which pipeline stage to run")
    parser.add_argument("--sample", type=int, default=None, help="Process only first N documents (for quick prototyping)")
    parser.add_argument("--no-gpu", action="store_true", help="Force CPU mode")
    args = parser.parse_args()

    ensure_dirs()

    if args.no_gpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    # Read CSV
    if DATA_CSV.exists():
        df = pd.read_csv(DATA_CSV)
    else:
        df = pd.DataFrame(columns=["id","title","link"])
        logger.warning("CSV %s not found. Create data/nasa_papers.csv", DATA_CSV)

    if args.mode == "download":
        download_papers(df, sample_n=args.sample)
        return
    if args.mode == "extract_text":
        run_text_extraction(sample_n=args.sample)
        return
    if args.mode == "extractive":
        run_extractive_for_all(sample_n=args.sample)
        return
    if args.mode == "abstractive":
        run_abstractive_for_all(sample_n=args.sample)
        return
    if args.mode == "entities":
        run_scispacy_for_all(sample_n=args.sample)
        return
    if args.mode == "embed":
        compute_embeddings_and_index(sample_n=args.sample)
        return
    if args.mode == "topic":
        run_bertopic(sample_n=args.sample)
        return
    if args.mode == "serve":
        # run Streamlit app (Note: to run streamlit from script you can just call streamlit CLI)
        # but we provide direct streamlit app run if script executed by streamlit
        streamlit_app()
        return

    # default: full pipeline
    logger.info("Running full pipeline: download -> extract -> extractive -> abstractive -> entities -> embed -> topic")
    download_papers(df, sample_n=args.sample)
    run_text_extraction(sample_n=args.sample)
    run_extractive_for_all(sample_n=args.sample)
    run_abstractive_for_all(sample_n=args.sample)
    run_scispacy_for_all(sample_n=args.sample)
    compute_embeddings_and_index(sample_n=args.sample)
    run_bertopic(sample_n=args.sample)
    logger.info("Pipeline complete. Use `python nasa_pipeline_all_in_one.py --mode serve` to run the Streamlit explorer.")
    

if __name__ == "__main__":
    main()

"""
END OF SCRIPT
"""