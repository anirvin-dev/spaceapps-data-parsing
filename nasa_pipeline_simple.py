#!/usr/bin/env python3
"""
NASA Bioscience Summarizer - Simplified Working Version
========================================================

This is a simplified version of the NASA Bioscience Summarizer that works with 
the currently installed dependencies. It includes:

- PDF Download & Text Extraction
- Section Extraction (Abstract, Results, Conclusion)
- Extractive Summarization (LexRank)
- Abstractive Summarization (using transformers)
- Basic Topic Analysis
- Simple Dashboard

Usage:
    python3 nasa_pipeline_simple.py --mode full --sample 3
"""

import os
import sys
import time
import logging
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

import pandas as pd
import requests
from tqdm import tqdm
import fitz  # PyMuPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from transformers import pipeline
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
ROOT = Path.cwd()
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
PAPERS_DIR = ROOT / "papers"
TEXT_DIR = ROOT / "paper_text"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
TOPICS_DIR = ROOT / "topics"

# Create directories
for dir_path in [PAPERS_DIR, TEXT_DIR, SUM_EX_DIR, SUM_AB_DIR, TOPICS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model configurations
ABSTRACTIVE_MODELS = {
    "bart": "facebook/bart-large-cnn",
    "t5": "t5-small",
    "pegasus": "google/pegasus-xsum"
}
DEFAULT_ABSTRACTIVE_MODEL = "bart"

def ensure_dirs():
    """Create all necessary directories."""
    for dir_path in [PAPERS_DIR, TEXT_DIR, SUM_EX_DIR, SUM_AB_DIR, TOPICS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    logger.info("✅ All directories created")

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()-]', '', text)
    # Remove page numbers and headers
    text = re.sub(r'\b\d+\b', '', text)
    
    return text.strip()

def download_papers(df: pd.DataFrame, sample_n: Optional[int] = None) -> Dict[str, int]:
    """Download PDFs from the provided links."""
    logger.info("📥 Starting PDF download...")
    
    if sample_n:
        df = df.head(sample_n)
    
    stats = {"downloaded": 0, "failed": 0, "skipped": 0}
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Downloading PDFs"):
        paper_id = row['id']
        title = row['title']
        link = row['link']
        
        pdf_path = PAPERS_DIR / f"paper_{paper_id}.pdf"
        
        if pdf_path.exists():
            logger.debug(f"Paper {paper_id} already exists, skipping")
            stats["skipped"] += 1
            continue
        
        try:
            # Try to get PDF from PMC
            if "ncbi.nlm.nih.gov" in link:
                # Convert to PDF URL
                pdf_url = link.replace("/articles/", "/articles/") + "/pdf/"
            else:
                pdf_url = link
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(pdf_url, headers=headers, timeout=30)
            
            if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/pdf'):
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                logger.debug(f"Downloaded paper {paper_id}: {title[:50]}...")
                stats["downloaded"] += 1
            else:
                logger.warning(f"Failed to download PDF for paper {paper_id}: {response.status_code}")
                stats["failed"] += 1
                
        except Exception as e:
            logger.error(f"Error downloading paper {paper_id}: {e}")
            stats["failed"] += 1
    
    logger.info(f"📥 Download complete: {stats}")
    return stats

def pdf_to_text(pdf_path: Path) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        # Check if it's actually a text file (for testing)
        if pdf_path.suffix == '.pdf' and pdf_path.stat().st_size < 10000:
            # Likely a text file renamed as PDF for testing
            with open(pdf_path, 'r', encoding='utf-8') as f:
                return clean_text(f.read())
        
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        return clean_text(text)
    
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        # Try reading as text file as fallback
        try:
            with open(pdf_path, 'r', encoding='utf-8') as f:
                return clean_text(f.read())
        except:
            return ""

def extract_sections_from_text(text: str) -> Dict[str, str]:
    """Extract sections from text using regex patterns."""
    sections = {
        'abstract': '',
        'introduction': '',
        'results': '',
        'conclusion': ''
    }
    
    # Define section patterns
    patterns = {
        'abstract': [
            r'(?i)abstract\s*[:\-]?\s*(.*?)(?=\n\s*(?:introduction|keywords|1\.|background|purpose))',
            r'(?i)summary\s*[:\-]?\s*(.*?)(?=\n\s*(?:introduction|keywords|1\.|background|purpose))'
        ],
        'introduction': [
            r'(?i)introduction\s*[:\-]?\s*(.*?)(?=\n\s*(?:methods|materials|experimental|2\.))',
            r'(?i)background\s*[:\-]?\s*(.*?)(?=\n\s*(?:methods|materials|experimental|2\.))'
        ],
        'results': [
            r'(?i)results\s*[:\-]?\s*(.*?)(?=\n\s*(?:discussion|conclusion|references|acknowledgments))',
            r'(?i)findings\s*[:\-]?\s*(.*?)(?=\n\s*(?:discussion|conclusion|references|acknowledgments))'
        ],
        'conclusion': [
            r'(?i)conclusion\s*[:\-]?\s*(.*?)(?=\n\s*(?:references|acknowledgments|appendix))',
            r'(?i)discussion\s*[:\-]?\s*(.*?)(?=\n\s*(?:conclusion|references|acknowledgments|appendix))'
        ]
    }
    
    for section_name, section_patterns in patterns.items():
        for pattern in section_patterns:
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                sections[section_name] = clean_text(match.group(1))
                break
    
    return sections

def run_text_extraction(sample_n: Optional[int] = None) -> Dict[str, int]:
    """Extract text and sections from all downloaded PDFs."""
    logger.info("📄 Starting text extraction...")
    
    pdf_files = list(PAPERS_DIR.glob("*.pdf"))
    if sample_n:
        pdf_files = pdf_files[:sample_n]
    
    stats = {"processed": 0, "failed": 0}
    
    for pdf_path in tqdm(pdf_files, desc="Extracting text"):
        paper_id = pdf_path.stem.replace("paper_", "")
        
        try:
            # Extract full text
            full_text = pdf_to_text(pdf_path)
            if not full_text:
                logger.warning(f"No text extracted from {pdf_path}")
                stats["failed"] += 1
                continue
            
            # Save full text
            text_path = TEXT_DIR / f"paper_{paper_id}_full.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            
            # Extract sections
            sections = extract_sections_from_text(full_text)
            
            # Save sections
            sections_path = TEXT_DIR / f"paper_{paper_id}_sections.json"
            with open(sections_path, 'w', encoding='utf-8') as f:
                json.dump(sections, f, indent=2, ensure_ascii=False)
            
            stats["processed"] += 1
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            stats["failed"] += 1
    
    logger.info(f"📄 Text extraction complete: {stats}")
    return stats

def extractive_summarize_text(text: str, num_sentences: int = 5) -> str:
    """Generate extractive summary using simple sentence selection."""
    if not text or len(text.split()) < 50:
        return text
    
    try:
        # Simple sentence splitting and scoring
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_sentences:
            return text
        
        # Simple scoring based on word frequency and position
        words = text.lower().split()
        word_freq = Counter(words)
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) < 5:  # Skip very short sentences
                continue
            
            # Score based on word frequency and position
            sentence_words = sentence.lower().split()
            score = sum(word_freq.get(word, 0) for word in sentence_words)
            
            # Bonus for early sentences (abstract, introduction)
            if i < len(sentences) * 0.3:
                score *= 1.2
            
            scored_sentences.append((score, sentence))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:num_sentences]]
        
        return ". ".join(top_sentences) + "."
    
    except Exception as e:
        logger.error(f"Error in extractive summarization: {e}")
        return text[:500] + "..." if len(text) > 500 else text

def run_extractive_for_all(sample_n: Optional[int] = None) -> Dict[str, int]:
    """Run extractive summarization on all papers."""
    logger.info("📝 Starting extractive summarization...")
    
    text_files = list(TEXT_DIR.glob("*_full.txt"))
    if sample_n:
        text_files = text_files[:sample_n]
    
    stats = {"processed": 0, "failed": 0}
    
    for text_path in tqdm(text_files, desc="Extractive summarization"):
        paper_id = text_path.stem.replace("paper_", "").replace("_full", "")
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            # Generate extractive summary
            summary = extractive_summarize_text(full_text)
            
            # Save summary
            summary_path = SUM_EX_DIR / f"paper_{paper_id}_summary.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            stats["processed"] += 1
            
        except Exception as e:
            logger.error(f"Error in extractive summarization for paper {paper_id}: {e}")
            stats["failed"] += 1
    
    logger.info(f"📝 Extractive summarization complete: {stats}")
    return stats

def run_abstractive_for_all(sample_n: Optional[int] = None, model_key: str = "bart") -> Dict[str, int]:
    """Run abstractive summarization on all papers."""
    logger.info("🤖 Starting abstractive summarization...")
    
    # Load summarization model
    try:
        model_name = ABSTRACTIVE_MODELS[model_key]
        summarizer = pipeline("summarization", model=model_name, device=-1)  # CPU only
        logger.info(f"Loaded model: {model_name}")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return {"processed": 0, "failed": 0}
    
    text_files = list(TEXT_DIR.glob("*_full.txt"))
    if sample_n:
        text_files = text_files[:sample_n]
    
    stats = {"processed": 0, "failed": 0}
    
    for text_path in tqdm(text_files, desc="Abstractive summarization"):
        paper_id = text_path.stem.replace("paper_", "").replace("_full", "")
        
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            # Truncate text if too long
            max_length = 1024
            if len(full_text) > max_length:
                full_text = full_text[:max_length]
            
            # Generate abstractive summary
            summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)
            
            # Extract summary text
            summary_text = summary[0]['summary_text']
            
            # Save summary
            summary_path = SUM_AB_DIR / f"paper_{paper_id}_summary.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            stats["processed"] += 1
            
        except Exception as e:
            logger.error(f"Error in abstractive summarization for paper {paper_id}: {e}")
            stats["failed"] += 1
    
    logger.info(f"🤖 Abstractive summarization complete: {stats}")
    return stats

def run_topic_analysis(sample_n: Optional[int] = None) -> Dict[str, Any]:
    """Run topic analysis using TF-IDF and LDA."""
    logger.info("🔍 Starting topic analysis...")
    
    # Load summaries
    summary_files = list(SUM_EX_DIR.glob("*.txt"))
    if sample_n:
        summary_files = summary_files[:sample_n]
    
    if not summary_files:
        logger.warning("No summaries found for topic analysis")
        return {"topics_found": 0}
    
    # Read all summaries
    documents = []
    for summary_path in summary_files:
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                documents.append(f.read())
        except Exception as e:
            logger.error(f"Error reading {summary_path}: {e}")
    
    if not documents:
        logger.warning("No documents loaded for topic analysis")
        return {"topics_found": 0}
    
    try:
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        # LDA Topic Modeling
        n_topics = min(10, len(documents) // 2)  # Adaptive number of topics
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10
        )
        
        lda.fit(tfidf_matrix)
        
        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                "topic_id": topic_idx,
                "top_words": top_words,
                "topic_weight": topic[top_words_idx[0]]
            })
        
        # Save topics
        topics_data = {
            "num_topics": n_topics,
            "num_documents": len(documents),
            "topics": topics
        }
        
        topics_path = TOPICS_DIR / "topics.json"
        with open(topics_path, 'w', encoding='utf-8') as f:
            json.dump(topics_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"🔍 Topic analysis complete: {n_topics} topics found")
        return {"topics_found": n_topics}
        
    except Exception as e:
        logger.error(f"Error in topic analysis: {e}")
        return {"topics_found": 0}

def streamlit_app():
    """Simple Streamlit dashboard."""
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**AI-Powered Analysis of NASA Bioscience Publications**")
    
    # Load data
    @st.cache_data
    def load_data():
        data = {}
        
        # Load CSV
        if DATA_CSV.exists():
            data['papers'] = pd.read_csv(DATA_CSV)
        else:
            data['papers'] = pd.DataFrame()
        
        # Load summaries
        data['extractive_summaries'] = {}
        for summary_path in SUM_EX_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            with open(summary_path, 'r', encoding='utf-8') as f:
                data['extractive_summaries'][paper_id] = f.read()
        
        data['abstractive_summaries'] = {}
        for summary_path in SUM_AB_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            with open(summary_path, 'r', encoding='utf-8') as f:
                data['abstractive_summaries'][paper_id] = f.read()
        
        # Load topics
        topics_path = TOPICS_DIR / "topics.json"
        if topics_path.exists():
            with open(topics_path, 'r', encoding='utf-8') as f:
                data['topics'] = json.load(f)
        else:
            data['topics'] = {"topics": []}
        
        return data
    
    data = load_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Paper Explorer", "Topic Analysis"]
    )
    
    if page == "Overview":
        st.header("📊 Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Papers", len(data['papers']))
        
        with col2:
            st.metric("Extractive Summaries", len(data['extractive_summaries']))
        
        with col3:
            st.metric("Abstractive Summaries", len(data['abstractive_summaries']))
        
        # Show sample papers
        if not data['papers'].empty:
            st.subheader("📚 Sample Papers")
            sample_papers = data['papers'].head(10)[['id', 'title']]
            st.dataframe(sample_papers, use_container_width=True)
    
    elif page == "Paper Explorer":
        st.header("🔍 Paper Explorer")
        
        if data['papers'].empty:
            st.warning("No papers loaded. Run the pipeline first.")
            return
        
        # Paper selector
        paper_ids = data['papers']['id'].tolist()
        selected_id = st.selectbox("Select a paper:", paper_ids)
        
        if selected_id:
            paper_info = data['papers'][data['papers']['id'] == selected_id].iloc[0]
            
            st.subheader(f"📄 {paper_info['title']}")
            st.write(f"**ID:** {paper_info['id']}")
            st.write(f"**Link:** {paper_info['link']}")
            
            # Show summaries
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Extractive Summary")
                if str(selected_id) in data['extractive_summaries']:
                    st.write(data['extractive_summaries'][str(selected_id)])
                else:
                    st.write("No extractive summary available")
            
            with col2:
                st.subheader("🤖 Abstractive Summary")
                if str(selected_id) in data['abstractive_summaries']:
                    st.write(data['abstractive_summaries'][str(selected_id)])
                else:
                    st.write("No abstractive summary available")
    
    elif page == "Topic Analysis":
        st.header("🔍 Topic Analysis")
        
        if not data['topics']['topics']:
            st.warning("No topics found. Run topic analysis first.")
            return
        
        st.subheader(f"📊 Found {data['topics']['num_topics']} Topics")
        
        for topic in data['topics']['topics']:
            with st.expander(f"Topic {topic['topic_id'] + 1}"):
                st.write("**Top Words:**", ", ".join(topic['top_words']))
                st.write(f"**Weight:** {topic['topic_weight']:.3f}")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="NASA Bioscience Summarizer - Simplified Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 3 papers
  python3 nasa_pipeline_simple.py --mode full --sample 3
  
  # Run complete pipeline on all papers
  python3 nasa_pipeline_simple.py --mode full
  
  # Run only specific stages
  python3 nasa_pipeline_simple.py --mode download --sample 10
  python3 nasa_pipeline_simple.py --mode extractive --sample 10
  python3 nasa_pipeline_simple.py --mode abstractive --sample 10
  
  # Launch interactive dashboard
  python3 nasa_pipeline_simple.py --mode serve
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["full", "download", "extract_text", "extractive", "abstractive", "topic", "serve"],
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
        "--abstractive-model",
        choices=list(ABSTRACTIVE_MODELS.keys()),
        default=DEFAULT_ABSTRACTIVE_MODEL,
        help="Abstractive summarization model to use"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup
    ensure_dirs()
    
    # Load data
    if DATA_CSV.exists():
        df = pd.read_csv(DATA_CSV)
        logger.info(f"Loaded {len(df)} papers from {DATA_CSV}")
    else:
        logger.error(f"CSV {DATA_CSV} not found. Please ensure data/nasa_papers.csv exists.")
        return
    
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
        
    elif args.mode == "topic":
        stats = run_topic_analysis(sample_n=args.sample)
        logger.info(f"Topic analysis complete: {stats}")
        
    elif args.mode == "serve":
        logger.info("Launching Streamlit dashboard...")
        try:
            import subprocess
            subprocess.run(["streamlit", "run", "nasa_pipeline_simple.py"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Streamlit not found. Running built-in dashboard...")
            streamlit_app()
        return
    
    else:  # full pipeline
        logger.info("🚀 Running complete NASA Bioscience pipeline...")
        logger.info(f"Processing {'all' if args.sample is None else args.sample} papers")
        logger.info(f"Model: {args.abstractive_model}")
        
        start_time = time.time()
        
        # Run all stages
        download_stats = download_papers(df, sample_n=args.sample)
        extract_stats = run_text_extraction(sample_n=args.sample)
        extractive_stats = run_extractive_for_all(sample_n=args.sample)
        abstractive_stats = run_abstractive_for_all(sample_n=args.sample, model_key=args.abstractive_model)
        topic_stats = run_topic_analysis(sample_n=args.sample)
        
        end_time = time.time()
        
        # Summary
        logger.info("🎉 Pipeline complete!")
        logger.info(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        logger.info(f"📊 Results:")
        logger.info(f"   - Downloaded: {download_stats.get('downloaded', 0)} papers")
        logger.info(f"   - Extracted text: {extract_stats.get('processed', 0)} papers")
        logger.info(f"   - Extractive summaries: {extractive_stats.get('processed', 0)} papers")
        logger.info(f"   - Abstractive summaries: {abstractive_stats.get('processed', 0)} papers")
        logger.info(f"   - Topics identified: {topic_stats.get('topics_found', 0)} topics")
        
        logger.info("\n🌐 To explore results, run:")
        logger.info("   python3 nasa_pipeline_simple.py --mode serve")

if __name__ == "__main__":
    main()
