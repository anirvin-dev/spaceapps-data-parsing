#!/usr/bin/env python3
"""
NASA Bioscience Summarizer - Streamlit Dashboard
================================================

This is a separate Streamlit dashboard for exploring the NASA Bioscience research results.

Usage:
    streamlit run dashboard_simple.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# Configuration
ROOT = Path.cwd()
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
TOPICS_DIR = ROOT / "topics"
TOPICS_JSON = TOPICS_DIR / "topics.json"

@st.cache_data
def load_dashboard_data():
    """Load all dashboard data."""
    data = {}
    
    # Load CSV
    if DATA_CSV.exists():
        data['papers'] = pd.read_csv(DATA_CSV)
    else:
        data['papers'] = pd.DataFrame()
    
    # Load summaries
    data['extractive_summaries'] = {}
    if SUM_EX_DIR.exists():
        for summary_path in SUM_EX_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    data['extractive_summaries'][paper_id] = f.read()
            except Exception as e:
                st.warning(f"Error loading summary {summary_path}: {e}")
    
    data['abstractive_summaries'] = {}
    if SUM_AB_DIR.exists():
        for summary_path in SUM_AB_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    data['abstractive_summaries'][paper_id] = f.read()
            except Exception as e:
                st.warning(f"Error loading summary {summary_path}: {e}")
    
    # Load topics
    data['topics'] = {"topics": []}
    if TOPICS_JSON.exists():
        try:
            with open(TOPICS_JSON, 'r', encoding='utf-8') as f:
                data['topics'] = json.load(f)
        except Exception as e:
            st.warning(f"Error loading topics: {e}")
    
    return data

def show_overview_page(data):
    """Display overview statistics."""
    st.header("📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Papers", len(data['papers']))
    
    with col2:
        st.metric("Extractive Summaries", len(data['extractive_summaries']))
    
    with col3:
        st.metric("Abstractive Summaries", len(data['abstractive_summaries']))
    
    with col4:
        st.metric("Topics Found", len(data['topics']['topics']))
    
    # Show sample papers
    if not data['papers'].empty:
        st.subheader("📚 Sample Papers")
        sample_papers = data['papers'].head(10)[['id', 'title']]
        st.dataframe(sample_papers, width='stretch')
    
    # Show processing status
    st.subheader("🔄 Processing Status")
    total_papers = len(data['papers'])
    processed_extractive = len(data['extractive_summaries'])
    processed_abstractive = len(data['abstractive_summaries'])
    
    if total_papers > 0:
        progress_extractive = processed_extractive / total_papers
        progress_abstractive = processed_abstractive / total_papers
        
        st.progress(progress_extractive, text=f"Extractive Summaries: {processed_extractive}/{total_papers}")
        st.progress(progress_abstractive, text=f"Abstractive Summaries: {processed_abstractive}/{total_papers}")

def show_paper_explorer(data):
    """Display paper explorer."""
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

def show_topic_analysis_page(data):
    """Display topic analysis."""
    st.header("🔍 Topic Analysis")
    
    if not data['topics']['topics']:
        st.warning("No topics found. Run topic analysis first.")
        return
    
    st.subheader(f"📊 Found {data['topics']['num_topics']} Topics")
    
    for topic in data['topics']['topics']:
        with st.expander(f"Topic {topic['topic_id'] + 1}"):
            st.write("**Top Words:**", ", ".join(topic['top_words']))
            st.write(f"**Weight:** {topic['topic_weight']:.3f}")
    
    # Create topic visualization
    if len(data['topics']['topics']) > 1:
        st.subheader("📈 Topic Distribution")
        
        topic_data = []
        for topic in data['topics']['topics']:
            topic_data.append({
                'Topic': f"Topic {topic['topic_id'] + 1}",
                'Top Words': ", ".join(topic['top_words'][:5]),
                'Weight': topic['topic_weight']
            })
        
        df_topics = pd.DataFrame(topic_data)
        fig = px.bar(df_topics, x='Topic', y='Weight', 
                    title='Topic Weights',
                    hover_data=['Top Words'])
        st.plotly_chart(fig, width='stretch')

def show_search_page(data):
    """Display search functionality."""
    st.header("🔎 Search Papers")
    
    if data['papers'].empty:
        st.warning("No papers loaded. Run the pipeline first.")
        return
    
    # Search input
    search_term = st.text_input("Search papers by title or content:")
    
    if search_term:
        # Search in titles
        matching_papers = data['papers'][
            data['papers']['title'].str.contains(search_term, case=False, na=False)
        ]
        
        if len(matching_papers) > 0:
            st.subheader(f"Found {len(matching_papers)} papers matching '{search_term}'")
            
            for _, paper in matching_papers.iterrows():
                with st.expander(f"📄 {paper['title']}"):
                    st.write(f"**ID:** {paper['id']}")
                    st.write(f"**Link:** {paper['link']}")
                    
                    # Show summaries if available
                    if str(paper['id']) in data['extractive_summaries']:
                        st.write("**Extractive Summary:**")
                        st.write(data['extractive_summaries'][str(paper['id'])])
                    
                    if str(paper['id']) in data['abstractive_summaries']:
                        st.write("**Abstractive Summary:**")
                        st.write(data['abstractive_summaries'][str(paper['id'])])
        else:
            st.write(f"No papers found matching '{search_term}'")

def show_uploader_page(data):
    """Upload a PDF or paste a URL and summarize it on the fly."""
    st.header("📤 Upload or Paste URL for On-the-fly Summary")
    
    import tempfile
    from transformers import pipeline
    import fitz
    
    @st.cache_resource
    def get_summarizer(model_key: str = 'facebook/bart-large-cnn'):
        return pipeline("summarization", model=model_key, device=-1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded = st.file_uploader("Upload a PDF (<= 20MB)", type=["pdf"])
    
    with col2:
        url = st.text_input("Or paste a URL (PDF or article page)")
    
    model_choice = st.selectbox("Model", ["facebook/bart-large-cnn", "t5-small", "google/pegasus-xsum"], index=0)
    
    def extract_text_from_pdf_bytes(data_bytes: bytes) -> str:
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(data_bytes)
                tmp.flush()
                doc = fitz.open(tmp.name)
                full = "".join([doc.load_page(i).get_text() for i in range(len(doc))])
                doc.close()
                return full
        except Exception:
            return ""
    
    def extract_text_from_url(u: str) -> str:
        try:
            r = requests.get(u, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            ctype = r.headers.get('content-type', '')
            if 'pdf' in ctype or u.lower().endswith('.pdf'):
                return extract_text_from_pdf_bytes(r.content)
            soup = BeautifulSoup(r.text, 'lxml')
            for t in soup(["script","style","nav","footer","header","form"]):
                t.decompose()
            return soup.get_text(separator='\n')
        except Exception:
            return ""
    
    run = st.button("Summarize")
    if run:
        with st.spinner("Summarizing..."):
            text = ""
            if uploaded is not None:
                text = extract_text_from_pdf_bytes(uploaded.read())
            elif url:
                text = extract_text_from_url(url)
            else:
                st.warning("Please upload a PDF or paste a URL")
                return
            text = (text or "").strip()
            if not text:
                st.error("Could not extract text from the source.")
                return
            # Truncate for model
            text = text[:3000]
            summarizer = get_summarizer(model_choice)
            out = summarizer(text, max_length=180, min_length=60, do_sample=False)
            st.subheader("🧾 Summary")
            st.write(out[0]['summary_text'])

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="NASA Bioscience Research Explorer",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**AI-Powered Analysis of NASA Bioscience Publications**")
    
    # Load data
    data = load_dashboard_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Paper Explorer", "Topic Analysis", "Search Papers", "Upload/URL Summarizer"]
    )
    
    if page == "Overview":
        show_overview_page(data)
    elif page == "Paper Explorer":
        show_paper_explorer(data)
    elif page == "Topic Analysis":
        show_topic_analysis_page(data)
    elif page == "Search Papers":
        show_search_page(data)
    elif page == "Upload/URL Summarizer":
        show_uploader_page(data)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**NASA Bioscience Summarizer**")
    st.sidebar.markdown("Built with Streamlit and AI")

if __name__ == "__main__":
    main()

