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
from collections import Counter
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

# ==================== UTILITY FUNCTIONS ====================

def ensure_dirs():
    """Create all necessary directories for the pipeline."""
    directories = [
        PAPERS_DIR, TEXT_DIR, SUM_EX_DIR, SUM_AB_DIR, 
        ENT_DIR, EMBED_DIR, TOPICS_DIR, DASHBOARD_DIR
    ]
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created/verified directories: {[str(d) for d in directories]}")

def load_model_safely(model_name: str, model_type: str = "transformers"):
    """Safely load models with error handling and fallbacks."""
    try:
        if model_type == "transformers":
            return AutoTokenizer.from_pretrained(model_name), AutoModelForSeq2SeqLM.from_pretrained(model_name)
        elif model_type == "sentence_transformer":
            return SentenceTransformer(model_name)
        elif model_type == "spacy":
            return spacy.load(model_name)
    except Exception as e:
        logger.warning(f"Failed to load {model_name}: {e}")
        return None

def clean_text(text: str) -> str:
    """Clean and normalize text for processing."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep scientific notation
    text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\{\}\+\-\*\/\=\<\>]', '', text)
    return text.strip()


# ==================== DATA DOWNLOAD AND EXTRACTION ====================

def download_papers(df: pd.DataFrame, sample_n: int = None) -> Dict[str, Any]:
    """
    Enhanced PDF download with better error handling and progress tracking.
    
    Args:
        df: DataFrame with paper metadata
        sample_n: Limit number of papers to process
        
    Returns:
        Dictionary with download statistics
    """
    logger.info("Starting PDF download process...")
    stats = {"downloaded": 0, "failed": 0, "html_saved": 0, "already_exists": 0}
    
    rows = df.itertuples(index=False)
    if sample_n:
        rows = list(rows)[:sample_n]
        logger.info(f"Processing sample of {sample_n} papers")
    
    for row in tqdm(rows, desc="Downloading papers"):
        try:
            # Extract metadata with flexible column names
            rid = getattr(row, "id", None) or getattr(row, "ID", None) or None
            title = getattr(row, "title", None) or getattr(row, "Title", None) or "untitled"
            link = getattr(row, "link", None) or getattr(row, "Link", None) or None
            pdf_path = getattr(row, "pdf_path", None) or None
            
            # Create safe filename
            safe_title = re.sub(r"[^\w\d\s-]+", "", str(title)).replace(" ", "_")[:60]
            fname = PAPERS_DIR / f"{rid or int(time.time())}_{safe_title}.pdf"
            
            # Check if file already exists
            if fname.exists():
                stats["already_exists"] += 1
                continue
            
            # Handle local PDF files
            if pdf_path and Path(pdf_path).exists():
                try:
                    import shutil
                    shutil.copy2(pdf_path, fname)
                    logger.info(f"Copied local PDF: {pdf_path} -> {fname}")
                    stats["downloaded"] += 1
                    continue
                except Exception as e:
                    logger.warning(f"Failed to copy {pdf_path}: {e}")
            
            # Download from URL
            if link:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(link, timeout=30, headers=headers, allow_redirects=True)
                    response.raise_for_status()
                    
                    content_type = response.headers.get("Content-Type", "").lower()
                    
                    if "application/pdf" in content_type or link.lower().endswith(".pdf"):
                        fname.write_bytes(response.content)
                        logger.info(f"Downloaded PDF: {title[:50]}...")
                        stats["downloaded"] += 1
                    else:
                        # Save HTML for manual inspection
                        html_fname = PAPERS_DIR / f"{rid or int(time.time())}_{safe_title}.html"
                        html_fname.write_text(response.text, encoding="utf-8")
                        logger.info(f"Saved HTML (not PDF): {title[:50]}...")
                        stats["html_saved"] += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to download {link}: {e}")
                    stats["failed"] += 1
            else:
                logger.warning(f"No link or PDF path for: {title}")
                stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"Unexpected error processing row: {e}")
            stats["failed"] += 1
    
    logger.info(f"Download complete. Stats: {stats}")
    return stats


def pdf_to_text(pdf_path: Path) -> str:
    """
    Enhanced PDF text extraction with better handling of scientific papers.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        doc = fitz.open(str(pdf_path))
        pages = []
        
        for page_num, page in enumerate(doc):
            try:
                # Extract text with layout preservation
                text = page.get_text("text")
                if text.strip():
                    pages.append(f"--- Page {page_num + 1} ---\n{text}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num + 1} of {pdf_path}: {e}")
                continue
        
        doc.close()
        full_text = "\n\n".join(pages)
        
        # Clean up the text
        full_text = clean_text(full_text)
        logger.info(f"Extracted {len(full_text)} characters from {pdf_path.name}")
        return full_text
        
    except Exception as e:
        logger.error(f"Could not open PDF {pdf_path}: {e}")
        return ""

def extract_sections_from_text(text: str) -> Dict[str, str]:
    """
    Enhanced section extraction for scientific papers.
    Uses multiple patterns to identify key sections.
    
    Args:
        text: Full text of the paper
        
    Returns:
        Dictionary with extracted sections
    """
    if not text:
        return {"abstract": ""}
    
    sections = {}
    text = text.replace("\r", "\n")
    
    # Define section patterns (case-insensitive, flexible matching)
    section_patterns = {
        'abstract': [
            r'(?i)(?:^|\n)\s*(abstract|summary)\s*\n(.*?)(?=\n\s*(?:introduction|background|keywords|key\s*words|1\.|introduction|background)\b)',
            r'(?i)(?:^|\n)\s*(abstract)\s*\n(.*?)(?=\n\s*(?:introduction|1\.|background)\b)'
        ],
        'results': [
            r'(?i)(?:^|\n)\s*(results|findings|main\s*results)\s*\n(.*?)(?=\n\s*(?:discussion|conclusion|references|acknowledg|figure|table)\b)',
            r'(?i)(?:^|\n)\s*(results)\s*\n(.*?)(?=\n\s*(?:discussion|conclusion|references)\b)'
        ],
        'conclusion': [
            r'(?i)(?:^|\n)\s*(conclusion|conclusions|discussion|summary)\s*\n(.*?)(?=\n\s*(?:references|acknowledg|funding|conflict|author)\b)',
            r'(?i)(?:^|\n)\s*(conclusion|discussion)\s*\n(.*?)(?=\n\s*(?:references|acknowledg)\b)'
        ],
        'introduction': [
            r'(?i)(?:^|\n)\s*(introduction|background)\s*\n(.*?)(?=\n\s*(?:methods|materials|experimental|results)\b)',
            r'(?i)(?:^|\n)\s*(introduction)\s*\n(.*?)(?=\n\s*(?:methods|results)\b)'
        ]
    }
    
    # Extract sections using patterns
    for section_name, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(2).strip()
                if len(content) > 100:  # Only keep substantial content
                    sections[section_name] = content
                    break
    
    # Fallback: if no sections found, use first part as abstract
    if not sections:
        # Try to find a reasonable abstract length (usually 150-300 words)
        words = text.split()
        if len(words) > 200:
            sections['abstract'] = ' '.join(words[:250])
        else:
            sections['abstract'] = text[:1500]
    
    # Ensure we have at least an abstract
    if 'abstract' not in sections:
        sections['abstract'] = text[:1500]
    
    logger.debug(f"Extracted sections: {list(sections.keys())}")
    return sections


def run_text_extraction(sample_n: int = None) -> Dict[str, Any]:
    """
    Enhanced text extraction with progress tracking and statistics.
    
    Args:
        sample_n: Limit number of files to process
        
    Returns:
        Dictionary with extraction statistics
    """
    logger.info("Starting text extraction from PDFs...")
    stats = {"processed": 0, "failed": 0, "total_text_length": 0}
    
    files = list(PAPERS_DIR.glob("*.pdf"))
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} PDFs")
    
    if not files:
        logger.warning(f"No PDF files found in {PAPERS_DIR}")
        return stats
    
    for pdf_file in tqdm(files, desc="Extracting text"):
        try:
            # Check if already processed
            text_file = TEXT_DIR / f"{pdf_file.stem}.txt"
            sections_file = TEXT_DIR / f"{pdf_file.stem}_sections.txt"
            
            if text_file.exists() and sections_file.exists():
                logger.debug(f"Already processed: {pdf_file.name}")
                continue
            
            # Extract text and sections
            full_text = pdf_to_text(pdf_file)
            if not full_text.strip():
                logger.warning(f"No text extracted from {pdf_file.name}")
                stats["failed"] += 1
                continue
            
            sections = extract_sections_from_text(full_text)
            
            # Save files
            text_file.write_text(full_text, encoding="utf-8")
            sections_file.write_text(json.dumps(sections, indent=2), encoding="utf-8")
            
            stats["processed"] += 1
            stats["total_text_length"] += len(full_text)
            
            logger.debug(f"Processed {pdf_file.name}: {len(full_text)} chars, {len(sections)} sections")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {e}")
            stats["failed"] += 1
    
    logger.info(f"Text extraction complete. Stats: {stats}")
    return stats


# ==================== SUMMARIZATION ====================

def extractive_summarize_text(text: str, sentences_count: int = 5, method: str = "lexrank") -> str:
    """
    Enhanced extractive summarization with multiple algorithms.
    
    Args:
        text: Input text to summarize
        sentences_count: Number of sentences in summary
        method: Summarization method ('lexrank', 'textrank', 'luhn')
        
    Returns:
        Extractive summary
    """
    if not text or len(text.strip()) < 100:
        return text[:500] if text else ""
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        
        if method == "lexrank":
            summarizer = LexRankSummarizer()
        elif method == "textrank":
            summarizer = TextRankSummarizer()
        else:
            summarizer = LexRankSummarizer()  # Default fallback
        
        # Get summary sentences
        summary_sentences = summarizer(parser.document, sentences_count)
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        
        return summary.strip()
        
    except Exception as e:
        logger.warning(f"Extractive summarization failed: {e}")
        # Fallback: return first few sentences
        sentences = text.split('. ')
        return '. '.join(sentences[:sentences_count]) + '.'

def run_extractive_for_all(sample_n: int = None, method: str = "lexrank") -> Dict[str, Any]:
    """
    Run extractive summarization on all processed papers.
    
    Args:
        sample_n: Limit number of files to process
        method: Summarization method to use
        
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Starting extractive summarization using {method}...")
    stats = {"processed": 0, "failed": 0, "total_summary_length": 0}
    
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} files")
    
    if not files:
        logger.warning(f"No section files found in {TEXT_DIR}")
        return stats
    
    for sections_file in tqdm(files, desc="Creating extractive summaries"):
        try:
            # Check if already processed
            output_file = SUM_EX_DIR / f"{sections_file.stem}_extractive.txt"
            if output_file.exists():
                logger.debug(f"Already processed: {sections_file.name}")
                continue
            
            # Load sections
            sections = json.loads(sections_file.read_text(encoding="utf-8"))
            
            # Prioritize results > conclusion > abstract for summarization
            text_to_summarize = ""
            for section in ['results', 'conclusion', 'abstract']:
                if section in sections and sections[section].strip():
                    text_to_summarize = sections[section]
                    break
            
            if not text_to_summarize.strip():
                logger.warning(f"No suitable text found for {sections_file.name}")
                stats["failed"] += 1
                continue
            
            # Create summary
            summary = extractive_summarize_text(text_to_summarize, sentences_count=5, method=method)
            
            if summary.strip():
                output_file.write_text(summary, encoding="utf-8")
                stats["processed"] += 1
                stats["total_summary_length"] += len(summary)
                logger.debug(f"Created summary for {sections_file.name}: {len(summary)} chars")
            else:
                logger.warning(f"Empty summary for {sections_file.name}")
                stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"Failed to process {sections_file.name}: {e}")
            stats["failed"] += 1
    
    logger.info(f"Extractive summarization complete. Stats: {stats}")
    return stats


def load_abstractive_model(model_key: str = DEFAULT_ABSTRACTIVE_MODEL):
    """
    Load abstractive summarization model with error handling and fallbacks.
    
    Args:
        model_key: Key for model selection
        
    Returns:
        Tuple of (tokenizer, model, device)
    """
    model_name = ABSTRACTIVE_MODELS.get(model_key, ABSTRACTIVE_MODELS[DEFAULT_ABSTRACTIVE_MODEL])
    logger.info(f"Loading abstractive model: {model_name}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        logger.info(f"Model loaded successfully on {device}")
        return tokenizer, model, device
    except Exception as e:
        logger.error(f"Failed to load {model_name}: {e}")
        # Fallback to a simpler model
        try:
            fallback_model = "facebook/bart-large-cnn"
            logger.info(f"Trying fallback model: {fallback_model}")
            tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            model = AutoModelForSeq2SeqLM.from_pretrained(fallback_model)
            device = "cpu"  # Use CPU for fallback
            model = model.to(device)
            return tokenizer, model, device
        except Exception as e2:
            logger.error(f"Fallback model also failed: {e2}")
            return None, None, None


def chunk_text_for_model(text: str, tokenizer, max_tokens: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Enhanced text chunking with better handling of scientific papers.
    
    Args:
        text: Input text to chunk
        tokenizer: Tokenizer for the model
        max_tokens: Maximum tokens per chunk
        overlap: Token overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or len(text.strip()) < 100:
        return [text] if text else []
    
    try:
        # Tokenize the text
        tokens = tokenizer(text, return_tensors="pt", truncation=False, add_special_tokens=False)
        input_ids = tokens["input_ids"][0]
        
        chunks = []
        start = 0
        total_length = input_ids.size(0)
        
        while start < total_length:
            end = min(start + max_tokens, total_length)
            
            # Extract chunk tokens
            chunk_tokens = input_ids[start:end]
            
            # Decode chunk
            chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            
            # Move start position with overlap
            start = end - overlap
            if start >= total_length:
                break
        
        return chunks if chunks else [text[:max_tokens*4]]  # Fallback
        
    except Exception as e:
        logger.warning(f"Chunking failed: {e}")
        # Simple fallback: split by sentences
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_tokens * 4:  # Rough estimate
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]

def summarize_chunk(chunk: str, tokenizer, model, device, max_len: int = CHUNK_SUM_MAXLEN) -> str:
    """
    Summarize a single text chunk using the abstractive model.
    
    Args:
        chunk: Text chunk to summarize
        tokenizer: Model tokenizer
        model: Abstractive model
        device: Device to run on
        max_len: Maximum length of summary
        
    Returns:
        Generated summary
    """
    try:
        # Prepare inputs
        inputs = tokenizer(
            chunk, 
            return_tensors="pt", 
            truncation=True, 
            max_length=tokenizer.model_max_length,
            padding=True
        ).to(device)
        
        # Generate summary
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_len,
                min_length=max_len//3,
                num_beams=NUM_BEAMS,
                early_stopping=True,
                temperature=TEMPERATURE,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )
        
        # Decode output
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return summary.strip()
        
    except Exception as e:
        logger.warning(f"Chunk summarization failed: {e}")
        # Fallback: return first few sentences
        sentences = chunk.split('. ')
        return '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else chunk[:500]

def run_abstractive_for_all(sample_n: int = None, model_key: str = DEFAULT_ABSTRACTIVE_MODEL) -> Dict[str, Any]:
    """
    Run abstractive summarization on all processed papers.
    
    Args:
        sample_n: Limit number of files to process
        model_key: Model to use for summarization
        
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Starting abstractive summarization using {model_key}...")
    stats = {"processed": 0, "failed": 0, "total_summary_length": 0}
    
    # Load model
    tokenizer, model, device = load_abstractive_model(model_key)
    if tokenizer is None or model is None:
        logger.error("Failed to load abstractive model")
        return stats
    
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} files")
    
    if not files:
        logger.warning(f"No section files found in {TEXT_DIR}")
        return stats
    
    for sections_file in tqdm(files, desc="Creating abstractive summaries"):
        try:
            # Check if already processed
            output_file = SUM_AB_DIR / f"{sections_file.stem}_abstractive.json"
            if output_file.exists():
                logger.debug(f"Already processed: {sections_file.name}")
                continue
            
            # Load sections
            sections = json.loads(sections_file.read_text(encoding="utf-8"))
            
            # Prioritize results > conclusion > abstract for summarization
            text_to_summarize = ""
            for section in ['results', 'conclusion', 'abstract']:
                if section in sections and sections[section].strip():
                    text_to_summarize = sections[section]
                    break
            
            if not text_to_summarize.strip():
                logger.warning(f"No suitable text found for {sections_file.name}")
                stats["failed"] += 1
                continue
            
            # Chunk text
            chunks = chunk_text_for_model(text_to_summarize, tokenizer)
            chunk_summaries = []
            
            # Summarize each chunk
            for i, chunk in enumerate(chunks):
                try:
                    chunk_summary = summarize_chunk(chunk, tokenizer, model, device)
                    chunk_summaries.append(chunk_summary)
                    logger.debug(f"Summarized chunk {i+1}/{len(chunks)} for {sections_file.name}")
                except Exception as e:
                    logger.warning(f"Chunk {i} summarization failed for {sections_file.name}: {e}")
                    chunk_summaries.append(chunk[:500])  # Fallback
            
            # Final summarization of chunk summaries
            if len(chunk_summaries) > 1:
                combined_chunks = "\n\n".join(chunk_summaries)
                try:
                    final_summary = summarize_chunk(combined_chunks, tokenizer, model, device, max_len=FINAL_SUM_MAXLEN)
                except Exception as e:
                    logger.warning(f"Final summarization failed for {sections_file.name}: {e}")
                    final_summary = " ".join(chunk_summaries)[:FINAL_SUM_MAXLEN*4]  # Fallback
            else:
                final_summary = chunk_summaries[0] if chunk_summaries else ""
            
            # Save results
            output_data = {
                "doc_id": sections_file.stem,
                "model_used": model_key,
                "model_name": ABSTRACTIVE_MODELS.get(model_key, "unknown"),
                "chunks_processed": len(chunks),
                "chunk_summaries": chunk_summaries,
                "final_summary": final_summary,
                "original_sections": list(sections.keys()),
                "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            output_file.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
            
            stats["processed"] += 1
            stats["total_summary_length"] += len(final_summary)
            logger.debug(f"Created abstractive summary for {sections_file.name}: {len(final_summary)} chars")
            
        except Exception as e:
            logger.error(f"Failed to process {sections_file.name}: {e}")
            stats["failed"] += 1
    
    logger.info(f"Abstractive summarization complete. Stats: {stats}")
    return stats


# ==================== ENTITY EXTRACTION ====================

def run_scispacy_for_all(sample_n: int = None, model_key: str = DEFAULT_SCISPACY_MODEL) -> Dict[str, Any]:
    """
    Run scientific entity extraction using scispaCy.
    
    Args:
        sample_n: Limit number of files to process
        model_key: scispaCy model to use
        
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Starting entity extraction using {model_key}...")
    stats = {"processed": 0, "failed": 0, "total_entities": 0}
    
    # Load scispaCy model
    model_name = SCISPACY_MODELS.get(model_key, SCISPACY_MODELS[DEFAULT_SCISPACY_MODEL])
    try:
        nlp = spacy.load(model_name)
        logger.info(f"Loaded scispaCy model: {model_name}")
    except Exception as e:
        logger.error(f"Failed to load scispaCy model {model_name}: {e}")
        return stats
    
    files = list(TEXT_DIR.glob("*_sections.txt"))
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} files")
    
    if not files:
        logger.warning(f"No section files found in {TEXT_DIR}")
        return stats
    
    for sections_file in tqdm(files, desc="Extracting entities"):
        try:
            # Check if already processed
            output_file = ENT_DIR / f"{sections_file.stem}_entities.json"
            if output_file.exists():
                logger.debug(f"Already processed: {sections_file.name}")
                continue
            
            # Load sections
            sections = json.loads(sections_file.read_text(encoding="utf-8"))
            
            # Combine text from multiple sections for better entity extraction
            combined_text = ""
            for section in ['results', 'conclusion', 'abstract', 'introduction']:
                if section in sections and sections[section].strip():
                    combined_text += sections[section] + " "
            
            if not combined_text.strip():
                logger.warning(f"No text found for entity extraction in {sections_file.name}")
                stats["failed"] += 1
                continue
            
            # Process text with scispaCy
            doc = nlp(combined_text)
            
            # Extract entities with additional information
            entities = []
            seen_entities = set()  # Avoid duplicates
            
            for ent in doc.ents:
                # Filter out very short or very long entities
                if len(ent.text.strip()) < 3 or len(ent.text.strip()) > 100:
                    continue
                
                # Avoid duplicates
                entity_key = (ent.text.lower(), ent.label_)
                if entity_key in seen_entities:
                    continue
                seen_entities.add(entity_key)
                
                entity_data = {
                    "text": ent.text.strip(),
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": getattr(ent, 'score', 1.0),  # If available
                    "description": get_entity_description(ent.label_)
                }
                entities.append(entity_data)
            
            # Limit entities per document
            if len(entities) > MAX_ENTITIES_PER_DOC:
                # Sort by confidence or length, then take top entities
                entities = sorted(entities, key=lambda x: len(x['text']), reverse=True)[:MAX_ENTITIES_PER_DOC]
            
            # Save results
            output_data = {
                "doc_id": sections_file.stem,
                "model_used": model_key,
                "model_name": model_name,
                "total_entities": len(entities),
                "entities": entities,
                "sections_processed": list(sections.keys()),
                "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            output_file.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
            
            stats["processed"] += 1
            stats["total_entities"] += len(entities)
            logger.debug(f"Extracted {len(entities)} entities from {sections_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to process {sections_file.name}: {e}")
            stats["failed"] += 1
    
    logger.info(f"Entity extraction complete. Stats: {stats}")
    return stats

def get_entity_description(label: str) -> str:
    """Get human-readable description for entity labels."""
    descriptions = {
        'CHEMICAL': 'Chemical compound or substance',
        'DISEASE': 'Medical condition or disease',
        'ORGAN': 'Body organ or anatomical structure',
        'ORGANISM': 'Living organism',
        'CELL_LINE': 'Cell line or cell type',
        'CELL_TYPE': 'Type of cell',
        'PROTEIN': 'Protein or enzyme',
        'GENE_OR_GENE_PRODUCT': 'Gene or gene product',
        'SIMPLE_CHEMICAL': 'Simple chemical compound',
        'ANATOMICAL_SYSTEM': 'Anatomical system',
        'ORGANISM_SUBDIVISION': 'Subdivision of organism',
        'DEVELOPING_ANATOMICAL_STRUCTURE': 'Developing anatomical structure',
        'IMMATERIAL_ANATOMICAL_ENTITY': 'Immaterial anatomical entity',
        'MULTI-TISSUE_STRUCTURE': 'Multi-tissue structure',
        'TISSUE': 'Biological tissue',
        'PATHOLOGICAL_FORMATION': 'Pathological formation'
    }
    return descriptions.get(label, f'Entity type: {label}')


# ==================== EMBEDDINGS AND TOPIC MODELING ====================

def compute_embeddings_and_index(sample_n: int = None, model_key: str = DEFAULT_EMBEDDING_MODEL) -> Dict[str, Any]:
    """
    Compute embeddings and create FAISS index for semantic search.
    
    Args:
        sample_n: Limit number of files to process
        model_key: Embedding model to use
        
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Computing embeddings using {model_key}...")
    stats = {"processed": 0, "failed": 0, "embedding_dimension": 0}
    
    # Load embedding model
    model_name = EMBEDDING_MODELS.get(model_key, EMBEDDING_MODELS[DEFAULT_EMBEDDING_MODEL])
    try:
        model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model: {model_name}")
    except Exception as e:
        logger.error(f"Failed to load embedding model {model_name}: {e}")
        return stats
    
    # Collect documents and texts
    docs = []
    texts = []
    files = list(SUM_EX_DIR.glob("*_extractive.txt"))
    
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} files")
    
    if not files:
        logger.warning("No extractive summaries found; run extractive summarization first.")
        return stats
    
    for summary_file in tqdm(files, desc="Loading summaries for embeddings"):
        try:
            text = summary_file.read_text(encoding="utf-8")
            if text.strip():
                docs.append({"id": summary_file.stem, "text": text})
                texts.append(text)
        except Exception as e:
            logger.warning(f"Failed to read {summary_file}: {e}")
            stats["failed"] += 1
    
    if not texts:
        logger.warning("No valid texts found for embedding")
        return stats
    
    try:
        # Compute embeddings
        logger.info(f"Computing embeddings for {len(texts)} documents...")
        embeddings = model.encode(
            texts, 
            show_progress_bar=True, 
            convert_to_numpy=True,
            batch_size=32
        )
        
        # Create FAISS index
        embedding_dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(embeddings.astype('float32'))
        
        # Save index and metadata
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        
        # Save document metadata
        with open(DOCINFO_JSON, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)
        
        stats["processed"] = len(texts)
        stats["embedding_dimension"] = embedding_dim
        
        logger.info(f"Created FAISS index with {len(texts)} documents, dimension {embedding_dim}")
        logger.info(f"Saved index to {FAISS_INDEX_PATH}")
        
    except Exception as e:
        logger.error(f"Failed to compute embeddings: {e}")
        stats["failed"] = len(texts)
    
    return stats

def run_bertopic(sample_n: int = None, model_key: str = DEFAULT_EMBEDDING_MODEL) -> Dict[str, Any]:
    """
    Run BERTopic clustering on document summaries.
    
    Args:
        sample_n: Limit number of files to process
        model_key: Embedding model to use
        
    Returns:
        Dictionary with processing statistics
    """
    logger.info(f"Running BERTopic clustering using {model_key}...")
    stats = {"processed": 0, "failed": 0, "topics_found": 0}
    
    # Load embedding model
    model_name = EMBEDDING_MODELS.get(model_key, EMBEDDING_MODELS[DEFAULT_EMBEDDING_MODEL])
    try:
        embedding_model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model for BERTopic: {model_name}")
    except Exception as e:
        logger.error(f"Failed to load embedding model {model_name}: {e}")
        return stats
    
    # Collect texts
    files = list(SUM_EX_DIR.glob("*_extractive.txt"))
    if sample_n:
        files = files[:sample_n]
        logger.info(f"Processing sample of {sample_n} files")
    
    if not files:
        logger.warning("No extractive summaries found; run extractive summarization first.")
        return stats
    
    texts = []
    doc_ids = []
    
    for summary_file in tqdm(files, desc="Loading texts for topic modeling"):
        try:
            text = summary_file.read_text(encoding="utf-8")
            if text.strip() and len(text.strip()) > 50:  # Filter very short texts
                texts.append(text)
                doc_ids.append(summary_file.stem)
        except Exception as e:
            logger.warning(f"Failed to read {summary_file}: {e}")
    
    if len(texts) < 5:
        logger.warning("Not enough texts for topic modeling (need at least 5)")
        return stats
    
    try:
        # Configure BERTopic
        from bertopic import BERTopic
        from umap import UMAP
        from hdbscan import HDBSCAN
        
        # UMAP for dimensionality reduction
        umap_model = UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric='cosine',
            random_state=42
        )
        
        # HDBSCAN for clustering
        hdbscan_model = HDBSCAN(
            min_cluster_size=MIN_TOPIC_SIZE,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        # Create BERTopic model
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            verbose=True,
            calculate_probabilities=True
        )
        
        # Fit the model
        logger.info(f"Fitting BERTopic on {len(texts)} documents...")
        topics, probabilities = topic_model.fit_transform(texts)
        
        # Get topic information
        topic_info = topic_model.get_topic_info()
        logger.info(f"Found {len(topic_info)} topics")
        
        # Save model and results
        topic_model.save(str(TOPICS_DIR / "bertopic_model"))
        
        # Prepare results for saving
        results = {
            "model_used": model_key,
            "model_name": model_name,
            "total_documents": len(texts),
            "topics_found": len(topic_info),
            "topic_info": topic_info.to_dict('records'),
            "document_topics": {doc_ids[i]: int(topics[i]) for i in range(len(doc_ids))},
            "topic_probabilities": {doc_ids[i]: probabilities[i].tolist() for i in range(len(doc_ids))},
            "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save results
        with open(TOPICS_JSON, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        stats["processed"] = len(texts)
        stats["topics_found"] = len(topic_info)
        
        # Log top topics
        logger.info("Top topics found:")
        for idx, row in topic_info.head(10).iterrows():
            logger.info(f"  Topic {row['Topic']}: {row['Count']} documents")
        
    except Exception as e:
        logger.error(f"BERTopic clustering failed: {e}")
        stats["failed"] = len(texts)
    
    logger.info(f"BERTopic clustering complete. Stats: {stats}")
    return stats


# ==================== STREAMLIT DASHBOARD ====================

def streamlit_app():
    """Enhanced Streamlit dashboard for exploring NASA bioscience papers."""
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**AI-Powered Analysis of NASA Bioscience Publications**")
    
    # Load data
    @st.cache_data
    def load_dashboard_data():
        data = {
            'papers': [],
            'summaries': {},
            'entities': {},
            'topics': {},
            'embeddings': None
        }
        
        # Load paper metadata
        if DATA_CSV.exists():
            df = pd.read_csv(DATA_CSV)
            data['papers'] = df.to_dict('records')
        
        # Load summaries
        for summary_file in SUM_EX_DIR.glob("*_extractive.txt"):
            doc_id = summary_file.stem.replace("_extractive", "")
            data['summaries'][doc_id] = summary_file.read_text()
        
        for summary_file in SUM_AB_DIR.glob("*_abstractive.json"):
            doc_id = summary_file.stem.replace("_abstractive", "")
            try:
                data['summaries'][doc_id + "_abstractive"] = json.loads(summary_file.read_text())
            except:
                pass
        
        # Load entities
        for entity_file in ENT_DIR.glob("*_entities.json"):
            doc_id = entity_file.stem.replace("_entities", "")
            try:
                data['entities'][doc_id] = json.loads(entity_file.read_text())
            except:
                pass
        
        # Load topics
        if TOPICS_JSON.exists():
            try:
                data['topics'] = json.loads(TOPICS_JSON.read_text())
            except:
                pass
        
        return data
    
    data = load_dashboard_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Paper Explorer", "Topic Analysis", "Entity Explorer", "Search Papers"]
    )
    
    if page == "Overview":
        show_overview_page(data)
    elif page == "Paper Explorer":
        show_paper_explorer(data)
    elif page == "Topic Analysis":
        show_topic_analysis_page(data)
    elif page == "Entity Explorer":
        show_entity_explorer_page(data)
    elif page == "Search Papers":
        show_search_page(data)

def show_overview_page(data):
    """Show overview dashboard."""
    st.header("📊 Pipeline Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Papers", len(data['papers']))
    
    with col2:
        st.metric("Processed Summaries", len(data['summaries']))
    
    with col3:
        st.metric("Entity Extractions", len(data['entities']))
    
    with col4:
        st.metric("Topics Identified", len(data['topics'].get('topic_info', [])))
    
    # Processing status chart
    st.subheader("Processing Status")
    status_data = {
        'Total Papers': len(data['papers']),
        'With Summaries': len(data['summaries']),
        'With Entities': len(data['entities'])
    }
    
    fig = px.pie(
        values=list(status_data.values()),
        names=list(status_data.keys()),
        title="Document Processing Status"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_paper_explorer(data):
    """Show paper exploration interface."""
    st.header("📄 Paper Explorer")
    
    # Paper selection
    if data['papers']:
        paper_options = {f"{p.get('id', 'N/A')} - {p.get('title', 'Untitled')[:50]}...": p for p in data['papers'][:50]}
        selected_paper = st.selectbox("Select a paper:", list(paper_options.keys()))
        
        if selected_paper:
            paper = paper_options[selected_paper]
            st.subheader(f"📄 {paper.get('title', 'Untitled')}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**ID:** {paper.get('id', 'N/A')}")
                st.write(f"**Link:** {paper.get('link', 'N/A')}")
                
                # Show summaries
                paper_id = str(paper.get('id', ''))
                if paper_id in data['summaries']:
                    st.subheader("📝 Extractive Summary")
                    st.write(data['summaries'][paper_id])
                
                abstractive_key = paper_id + "_abstractive"
                if abstractive_key in data['summaries']:
                    st.subheader("🤖 Abstractive Summary")
                    abstractive_data = data['summaries'][abstractive_key]
                    if isinstance(abstractive_data, dict):
                        st.write(abstractive_data.get('final_summary', ''))
            
            with col2:
                # Show entities
                if paper_id in data['entities']:
                    st.subheader("🧬 Key Entities")
                    entities_data = data['entities'][paper_id]
                    if isinstance(entities_data, dict) and 'entities' in entities_data:
                        for entity in entities_data['entities'][:10]:
                            st.markdown(f"**{entity.get('text', '')}** ({entity.get('label', '')})")

def show_topic_analysis_page(data):
    """Show topic analysis page."""
    st.header("🎯 Topic Analysis")
    
    if not data['topics'] or 'topic_info' not in data['topics']:
        st.warning("No topic analysis data available. Run the pipeline first.")
        return
    
    topic_info = data['topics']['topic_info']
    
    # Topic distribution
    st.subheader("Topic Distribution")
    df_topics = pd.DataFrame(topic_info)
    
    fig = px.bar(
        df_topics.head(15),
        x='Count',
        y='Name',
        orientation='h',
        title="Top 15 Topics by Document Count"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_entity_explorer_page(data):
    """Show entity exploration page."""
    st.header("🧬 Entity Explorer")
    
    if not data['entities']:
        st.warning("No entity data available. Run the pipeline first.")
        return
    
    # Collect all entities
    all_entities = []
    for entities_data in data['entities'].values():
        if isinstance(entities_data, dict) and 'entities' in entities_data:
            all_entities.extend(entities_data['entities'])
    
    if not all_entities:
        st.warning("No entities found.")
        return
    
    # Entity type distribution
    entity_types = [e.get('label', 'UNKNOWN') for e in all_entities if isinstance(e, dict)]
    type_counts = Counter(entity_types)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entity Types")
        fig = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            title="Entity Type Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Most Common Entities")
        entity_texts = [e.get('text', '') for e in all_entities if isinstance(e, dict)]
        entity_counts = Counter(entity_texts)
        top_entities = entity_counts.most_common(10)
        
        fig = px.bar(
            x=[e[1] for e in top_entities],
            y=[e[0] for e in top_entities],
            orientation='h',
            title="Top 10 Entities"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_search_page(data):
    """Show search interface."""
    st.header("🔍 Search Papers")
    
    search_query = st.text_input("Search papers:", placeholder="Enter keywords, paper titles, or topics...")
    
    if search_query:
        query_lower = search_query.lower()
        matching_papers = [
            paper for paper in data['papers']
            if query_lower in str(paper.get('title', '')).lower() or
               query_lower in str(data['summaries'].get(paper.get('id', ''), '')).lower()
        ]
        
        st.write(f"Found {len(matching_papers)} matching papers")
        
        for paper in matching_papers[:10]:  # Show top 10
            with st.expander(f"📄 {paper.get('title', 'Untitled')}"):
                st.write(f"**ID:** {paper.get('id', 'N/A')}")
                st.write(f"**Link:** {paper.get('link', 'N/A')}")
                
                paper_id = str(paper.get('id', ''))
                if paper_id in data['summaries']:
                    st.write("**Summary:**")
                    st.write(data['summaries'][paper_id][:300] + "..." if len(data['summaries'][paper_id]) > 300 else data['summaries'][paper_id])


# ==================== MAIN CLI INTERFACE ====================

def main():
    """Main CLI interface for the NASA Bioscience Summarizer pipeline."""
    parser = argparse.ArgumentParser(
        description="NASA Bioscience Summarizer - Complete AI Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 3 papers
  python nasa_pipeline_all_in_one.py --mode full --sample 3
  
  # Run complete pipeline on all papers
  python nasa_pipeline_all_in_one.py --mode full
  
  # Run only specific stages
  python nasa_pipeline_all_in_one.py --mode download --sample 10
  python nasa_pipeline_all_in_one.py --mode extractive --sample 10
  python nasa_pipeline_all_in_one.py --mode abstractive --sample 10
  
  # Launch interactive dashboard
  python nasa_pipeline_all_in_one.py --mode serve
  # Or: streamlit run dashboard.py
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=[
            "full", "download", "extract_text", "extractive", 
            "abstractive", "entities", "embed", "topic", "serve"
        ], 
        default="full",
        help="Pipeline stage to run"
    )
    parser.add_argument(
        "--sample", 
        type=int, 
        default=None, 
        help="Process only first N documents (for quick testing)"
    )
    parser.add_argument(
        "--no-gpu", 
        action="store_true", 
        help="Force CPU mode (disable GPU acceleration)"
    )
    parser.add_argument(
        "--abstractive-model",
        choices=list(ABSTRACTIVE_MODELS.keys()),
        default=DEFAULT_ABSTRACTIVE_MODEL,
        help="Abstractive summarization model to use"
    )
    parser.add_argument(
        "--embedding-model",
        choices=list(EMBEDDING_MODELS.keys()),
        default=DEFAULT_EMBEDDING_MODEL,
        help="Embedding model to use"
    )
    parser.add_argument(
        "--scispacy-model",
        choices=list(SCISPACY_MODELS.keys()),
        default=DEFAULT_SCISPACY_MODEL,
        help="scispaCy model to use"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup
    ensure_dirs()
    
    if args.no_gpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        logger.info("GPU disabled - using CPU only")
    
    # Load data
    if DATA_CSV.exists():
        df = pd.read_csv(DATA_CSV)
        logger.info(f"Loaded {len(df)} papers from {DATA_CSV}")
    else:
        df = pd.DataFrame(columns=["id", "title", "link"])
        logger.warning(f"CSV {DATA_CSV} not found. Create data/nasa_papers.csv with columns: id, title, link")
    
    # Execute pipeline stages
    if args.mode == "download":
        stats = download_papers(df, sample_n=args.sample)
        logger.info(f"Download complete: {stats}")
        
    elif args.mode == "extract_text":
        stats = run_text_extraction(sample_n=args.sample)
        logger.info(f"Text extraction complete: {stats}")
        
    elif args.mode == "extractive":
        stats = run_extractive_for_all(sample_n=args.sample)
        logger.info(f"Extractive summarization complete: {stats}")
        
    elif args.mode == "abstractive":
        stats = run_abstractive_for_all(sample_n=args.sample, model_key=args.abstractive_model)
        logger.info(f"Abstractive summarization complete: {stats}")
        
    elif args.mode == "entities":
        stats = run_scispacy_for_all(sample_n=args.sample, model_key=args.scispacy_model)
        logger.info(f"Entity extraction complete: {stats}")
        
    elif args.mode == "embed":
        stats = compute_embeddings_and_index(sample_n=args.sample, model_key=args.embedding_model)
        logger.info(f"Embedding computation complete: {stats}")
        
    elif args.mode == "topic":
        stats = run_bertopic(sample_n=args.sample, model_key=args.embedding_model)
        logger.info(f"Topic modeling complete: {stats}")
        
    elif args.mode == "serve":
        logger.info("Launching Streamlit dashboard...")
        try:
            import subprocess
            subprocess.run(["streamlit", "run", "dashboard.py"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Streamlit not found. Running built-in dashboard...")
            streamlit_app()
        return
    
    else:  # full pipeline
        logger.info("🚀 Running complete NASA Bioscience pipeline...")
        logger.info(f"Processing {'all' if args.sample is None else args.sample} papers")
        logger.info(f"Models: {args.abstractive_model}, {args.embedding_model}, {args.scispacy_model}")
        
        start_time = time.time()
        
        # Run all stages
        download_stats = download_papers(df, sample_n=args.sample)
        extract_stats = run_text_extraction(sample_n=args.sample)
        extractive_stats = run_extractive_for_all(sample_n=args.sample)
        abstractive_stats = run_abstractive_for_all(sample_n=args.sample, model_key=args.abstractive_model)
        entity_stats = run_scispacy_for_all(sample_n=args.sample, model_key=args.scispacy_model)
        embedding_stats = compute_embeddings_and_index(sample_n=args.sample, model_key=args.embedding_model)
        topic_stats = run_bertopic(sample_n=args.sample, model_key=args.embedding_model)
        
        end_time = time.time()
        
        # Summary
        logger.info("🎉 Pipeline complete!")
        logger.info(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        logger.info(f"📊 Results:")
        logger.info(f"   - Downloaded: {download_stats.get('downloaded', 0)} papers")
        logger.info(f"   - Extracted text: {extract_stats.get('processed', 0)} papers")
        logger.info(f"   - Extractive summaries: {extractive_stats.get('processed', 0)} papers")
        logger.info(f"   - Abstractive summaries: {abstractive_stats.get('processed', 0)} papers")
        logger.info(f"   - Entity extractions: {entity_stats.get('processed', 0)} papers")
        logger.info(f"   - Embeddings computed: {embedding_stats.get('processed', 0)} papers")
        logger.info(f"   - Topics identified: {topic_stats.get('topics_found', 0)} topics")
        
        logger.info("\n🌐 To explore results, run:")
        logger.info("   python nasa_pipeline_all_in_one.py --mode serve")
        logger.info("   # or: streamlit run dashboard.py")

if __name__ == "__main__":
    main()

"""
END OF SCRIPT
"""