#!/usr/bin/env python3
"""
NASA Bioscience Summarizer - Complete Dashboard
===============================================

Complete dashboard with ALL features including paper summaries.

Usage:
    streamlit run dashboard_complete.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Configuration
ROOT = Path.cwd()
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
TOPICS_DIR = ROOT / "topics"
ANALYSIS_DIR = ROOT / "analysis"
TEXT_DIR = ROOT / "paper_text"
ADDITIONAL_DATA_DIR = ROOT / "additional_data"

@st.cache_data
def load_dashboard_data():
    """Load all dashboard data."""
    data = {}
    
    # Load CSV
    if DATA_CSV.exists():
        data['papers'] = pd.read_csv(DATA_CSV)
    else:
        data['papers'] = pd.DataFrame()
    
    # Load additional sources
    additional_csv = ADDITIONAL_DATA_DIR / "additional_sources.csv"
    if additional_csv.exists():
        data['additional_sources'] = pd.read_csv(additional_csv)
    else:
        data['additional_sources'] = pd.DataFrame()
    
    # Load summaries
    data['extractive_summaries'] = {}
    if SUM_EX_DIR.exists():
        for summary_path in SUM_EX_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    data['extractive_summaries'][paper_id] = f.read()
            except Exception:
                pass
    
    data['abstractive_summaries'] = {}
    if SUM_AB_DIR.exists():
        for summary_path in SUM_AB_DIR.glob("*.txt"):
            paper_id = summary_path.stem.replace("paper_", "").replace("_summary", "")
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    data['abstractive_summaries'][paper_id] = f.read()
            except Exception:
                pass
    
    # Load topics
    data['topics'] = {"topics": []}
    topics_json = TOPICS_DIR / "topics.json"
    if topics_json.exists():
        try:
            with open(topics_json, 'r', encoding='utf-8') as f:
                data['topics'] = json.load(f)
        except Exception:
            pass
    
    # Load advanced analysis
    data['claims'] = {"claims": {}}
    claims_json = ANALYSIS_DIR / "claims.json"
    if claims_json.exists():
        try:
            with open(claims_json, 'r', encoding='utf-8') as f:
                data['claims'] = json.load(f)
        except Exception:
            pass
    
    data['knowledge_gaps'] = {"gaps": []}
    gaps_json = ANALYSIS_DIR / "knowledge_gaps.json"
    if gaps_json.exists():
        try:
            with open(gaps_json, 'r', encoding='utf-8') as f:
                data['knowledge_gaps'] = json.load(f)
        except Exception:
            pass
    
    data['mission_insights'] = {"insights": []}
    mission_json = ANALYSIS_DIR / "mission_insights.json"
    if mission_json.exists():
        try:
            with open(mission_json, 'r', encoding='utf-8') as f:
                data['mission_insights'] = json.load(f)
        except Exception:
            pass
    
    return data

def show_overview_page(data):
    """Display overview statistics."""
    st.header("📊 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_papers = len(data['papers'])
    additional_sources = len(data['additional_sources'])
    
    with col1:
        st.metric("Total Papers", total_papers)
    
    with col2:
        st.metric("Additional NASA Sources", additional_sources)
    
    with col3:
        st.metric("Extractive Summaries", len(data['extractive_summaries']))
    
    with col4:
        st.metric("Abstractive Summaries", len(data['abstractive_summaries']))
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Claims", len(data['claims'].get('claims', {})))
    
    with col2:
        st.metric("Knowledge Gaps", len(data['knowledge_gaps'].get('gaps', [])))
    
    with col3:
        st.metric("Mission Insights", len(data['mission_insights'].get('insights', [])))
    
    with col4:
        st.metric("Total Data Sources", total_papers + additional_sources)
    
    # Show processing status
    st.subheader("🔄 Processing Status")
    if total_papers > 0:
        ext = len(data['extractive_summaries'])
        abs_sum = len(data['abstractive_summaries'])
        st.progress(ext/total_papers, text=f"Extractive: {ext}/{total_papers}")
        st.progress(abs_sum/total_papers, text=f"Abstractive: {abs_sum}/{total_papers}")
    
    # Additional sources breakdown
    if not data['additional_sources'].empty:
        st.subheader("🌐 Additional NASA Data Sources")
        source_counts = data['additional_sources']['source'].value_counts()
        fig = px.bar(x=source_counts.index, y=source_counts.values,
                     labels={'x': 'Source', 'y': 'Count'},
                     title="Data Sources Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_paper_explorer(data):
    """Browse and explore individual papers."""
    st.header("📄 Paper Explorer")
    
    if data['papers'].empty:
        st.warning("No papers loaded")
        return
    
    # Search/filter
    search = st.text_input("🔍 Search papers by title or ID:")
    
    papers = data['papers'].copy()
    if search:
        papers = papers[papers['title'].str.contains(search, case=False, na=False) | 
                       papers['id'].astype(str).str.contains(search, na=False)]
    
    st.write(f"Showing {len(papers)} papers")
    
    # Pagination
    papers_per_page = 10
    total_pages = (len(papers) - 1) // papers_per_page + 1
    page = st.selectbox("Page", range(1, total_pages + 1))
    
    start = (page - 1) * papers_per_page
    end = start + papers_per_page
    page_papers = papers.iloc[start:end]
    
    for _, paper in page_papers.iterrows():
        paper_id = str(paper['id'])
        
        with st.expander(f"📄 Paper {paper_id}: {paper['title'][:80]}..."):
            st.markdown(f"**Title:** {paper['title']}")
            st.markdown(f"**Link:** [{paper['link']}]({paper['link']})")
            st.markdown(f"**Paper ID:** {paper_id}")
            
            # Show summaries if available
            if paper_id in data['extractive_summaries']:
                st.subheader("📝 Extractive Summary")
                st.info(data['extractive_summaries'][paper_id])
            
            if paper_id in data['abstractive_summaries']:
                st.subheader("🤖 Abstractive Summary")
                st.success(data['abstractive_summaries'][paper_id])
            
            if paper_id not in data['extractive_summaries'] and paper_id not in data['abstractive_summaries']:
                st.warning("⏳ Summaries not yet generated for this paper")

def show_topic_analysis(data):
    """Display topic analysis."""
    st.header("🏷️ Topic Analysis")
    
    topics = data['topics'].get('topics', [])
    
    if not topics:
        st.warning("No topics generated yet. Run topic modeling first.")
        st.code("python3 nasa_pipeline_simple.py --mode topic")
        return
    
    st.subheader(f"📊 {len(topics)} Topics Identified")
    
    # Sort topics by ID to ensure consistent ordering
    topics_sorted = sorted(topics, key=lambda x: x.get('topic_id', 0))
    
    for idx, topic in enumerate(topics_sorted, start=1):
        topic_id = idx  # Use 1-based indexing
        top_words = topic.get('top_words', [])
        
        with st.expander(f"🔬 Topic {topic_id}: {', '.join(top_words[:5])}"):
            st.markdown("**Top Keywords:**")
            st.write(", ".join(top_words[:15]))
            
            if 'representative_docs' in topic:
                st.markdown("**📄 Representative Papers (Source Analysis):**")
                rep_docs = topic['representative_docs'][:5]  # Show up to 5
                for doc_id in rep_docs:
                    # Try to get paper title
                    if not data['papers'].empty:
                        paper = data['papers'][data['papers']['id'] == int(doc_id)]
                        if not paper.empty:
                            title = paper.iloc[0]['title']
                            st.write(f"- **Paper {doc_id}:** {title[:80]}...")
                        else:
                            st.write(f"- Paper {doc_id}")
                    else:
                        st.write(f"- Paper {doc_id}")
            
            # Show paper count for this topic
            if 'representative_docs' in topic:
                st.markdown(f"*Total papers in this topic: {len(topic['representative_docs'])}*")

def show_search_page(data):
    """Search papers by keywords."""
    st.header("🔍 Search Papers")
    
    search_term = st.text_input("Enter keywords (space-separated):")
    
    if search_term:
        # Search in titles
        results = data['papers'][
            data['papers']['title'].str.contains(search_term, case=False, na=False)
        ]
        
        # Also search in summaries
        summary_matches = []
        for paper_id, summary in data['extractive_summaries'].items():
            if search_term.lower() in summary.lower():
                summary_matches.append(int(paper_id))
        
        if summary_matches:
            summary_results = data['papers'][data['papers']['id'].isin(summary_matches)]
            results = pd.concat([results, summary_results]).drop_duplicates()
        
        st.write(f"Found {len(results)} papers matching '{search_term}'")
        
        for _, paper in results.iterrows():
            paper_id = str(paper['id'])
            with st.expander(f"📄 {paper['title'][:80]}..."):
                st.markdown(f"**Link:** [{paper['link']}]({paper['link']})")
                if paper_id in data['abstractive_summaries']:
                    st.success(data['abstractive_summaries'][paper_id])

def show_consensus_page(data):
    """Display consensus claims."""
    st.header("🤝 Consensus & Evidence Analysis")
    
    claims = data['claims'].get('claims', {})
    
    if not claims:
        st.warning("No consensus data available.")
        st.info("💡 Using demo data. Run `python3 create_demo_analysis.py` to regenerate.")
        return
    
    st.subheader(f"📊 {len(claims)} Scientific Claims")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        min_conf = st.slider("Min Confidence", 0, 100, 50)
    with col2:
        badge = st.selectbox("Badge", ["All", "strong_consensus", "moderate_consensus"], index=0)
    
    # Filter & sort
    filtered = [(k, v) for k, v in claims.items() 
                if v['consensus_score'] >= min_conf and (badge == "All" or v['confidence_badge'] == badge)]
    filtered.sort(key=lambda x: x[1]['consensus_score'], reverse=True)
    
    # Display
    for norm, claim_data in filtered:
        badge_icon = {"strong_consensus": "🟢", "moderate_consensus": "🟡", "weak_consensus": "🟠"}.get(claim_data['confidence_badge'], "⚪")
        
        with st.expander(f"{badge_icon} {claim_data['claim'].title()} ({claim_data['consensus_score']}%)"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Supporting", claim_data['supporting_papers'])
            c2.metric("Contradicting", claim_data['contradicting_papers'])
            c3.metric("Score", f"{claim_data['consensus_score']}%")
            
            st.subheader("📝 Evidence")
            for s in claim_data['supporting_snippets']:
                st.markdown(f"**Paper {s['paper_id']}** ({s['section']})")
                st.info(s['sentence'])

def show_knowledge_gaps_page(data):
    """Display knowledge gaps."""
    st.header("🔍 Knowledge Gap Detection")
    
    gaps = data['knowledge_gaps'].get('gaps', [])
    
    if not gaps:
        st.warning("No gap data.")
        st.info("💡 Using demo data. Run `python3 create_demo_analysis.py` to regenerate.")
        return
    
    st.subheader(f"📊 {len(gaps)} Identified Gaps")
    st.markdown("*High mission relevance + low research density*")
    
    for gap in gaps:
        icon = "🔴" if gap['gap_score'] > 0.7 else "🟡" if gap['gap_score'] > 0.5 else "🟢"
        
        with st.expander(f"{icon} Gap {gap['gap_score']:.2f} - {', '.join(gap['keywords'][:5])}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Relevance", f"{gap['mission_relevance']*100:.0f}%")
            c2.metric("Density", gap['paper_density'])
            c3.metric("Gap Score", f"{gap['gap_score']:.2f}")
            
            st.subheader("🔬 Recommended Experiments")
            for exp in gap['recommended_experiments']:
                st.markdown(f"- {exp}")

def show_mission_insights_page(data):
    """Display mission insights."""
    st.header("🚀 Mission Insights & Recommendations")
    
    insights = data['mission_insights'].get('insights', [])
    
    if not insights:
        st.warning("No insights.")
        st.info("💡 Using demo data. Run `python3 create_demo_analysis.py` to regenerate.")
        return
    
    st.subheader(f"📊 {len(insights)} Actionable Insights")
    
    # Filters
    col1, col2 = st.columns(2)
    categories = ["All"] + list(set(i['category'] for i in insights))
    with col1:
        cat_filter = st.selectbox("Category", categories)
    with col2:
        risk_filter = st.selectbox("Risk", ["All", "high", "medium", "low"])
    
    # Filter
    filtered = insights
    if cat_filter != "All":
        filtered = [i for i in filtered if i['category'] == cat_filter]
    if risk_filter != "All":
        filtered = [i for i in filtered if i['risk_level'] == risk_filter]
    
    # Display
    for insight in filtered:
        risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(insight['risk_level'], "⚪")
        
        with st.expander(f"{risk_icon} {insight['title']} - {insight['category']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Risk", insight['risk_level'].upper())
            c2.metric("Confidence", f"{insight['confidence']:.1f}%")
            c3.metric("Papers", insight['supporting_papers'])
            
            st.subheader("📋 Finding")
            st.info(insight['finding'])
            
            st.subheader("💡 Recommendation")
            st.success(insight['recommendation'])

def show_additional_sources_page(data):
    """Display additional NASA data sources."""
    st.header("🌐 Additional NASA Data Sources")
    
    if data['additional_sources'].empty:
        st.warning("No additional sources scraped yet.")
        st.code("python3 nasa_data_scraper.py --source all --limit 100")
        return
    
    sources = data['additional_sources']
    
    st.subheader(f"📊 {len(sources)} Additional Sources Integrated")
    
    # Filter by source type
    source_type = st.selectbox("Filter by Source", 
                               ["All"] + list(sources['source'].unique()))
    
    if source_type != "All":
        sources = sources[sources['source'] == source_type]
    
    st.write(f"Showing {len(sources)} sources")
    
    # Display sources
    for _, source in sources.iterrows():
        # Handle NaN/float titles
        title = str(source['title']) if pd.notna(source['title']) else "Untitled"
        
        # Handle both 'id' and 'source_id' columns
        if 'source_id' in source and pd.notna(source['source_id']):
            source_id = str(source['source_id'])
        elif 'id' in source and pd.notna(source['id']):
            source_id = str(source['id'])
        else:
            source_id = "N/A"
        
        title_short = title[:80] + "..." if len(title) > 80 else title
        
        with st.expander(f"🔬 {source_id}: {title_short}"):
            st.markdown(f"**Title:** {title}")
            st.markdown(f"**Source:** {source['source']}")
            st.markdown(f"**Type:** {source['type']}")
            st.markdown(f"**Category:** {source['category']}")
            st.markdown(f"**Link:** [{source['url']}]({source['url']})")

def main():
    """Main app."""
    st.set_page_config(
        page_title="NASA Bioscience Research Explorer",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**Comprehensive AI-Powered Analysis of 600+ NASA Research Sources**")
    
    data = load_dashboard_data()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Paper Explorer", "Topic Analysis", "Search Papers",
         "Consensus Claims", "Knowledge Gaps", "Mission Insights", "Additional NASA Sources"]
    )
    
    if page == "Overview":
        show_overview_page(data)
    elif page == "Paper Explorer":
        show_paper_explorer(data)
    elif page == "Topic Analysis":
        show_topic_analysis(data)
    elif page == "Search Papers":
        show_search_page(data)
    elif page == "Consensus Claims":
        show_consensus_page(data)
    elif page == "Knowledge Gaps":
        show_knowledge_gaps_page(data)
    elif page == "Mission Insights":
        show_mission_insights_page(data)
    elif page == "Additional NASA Sources":
        show_additional_sources_page(data)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**✨ Features:**")
    st.sidebar.markdown("- 📄 Paper Summaries (Extract + Abstract)")
    st.sidebar.markdown("- 🤝 Evidence-backed Consensus")
    st.sidebar.markdown("- 🔍 Knowledge Gap Detection")
    st.sidebar.markdown("- 🚀 Mission Recommendations")
    st.sidebar.markdown("- 🌐 Multi-Source Integration")
    st.sidebar.markdown("- 🏷️ Topic Clustering")
    st.sidebar.markdown("- 🔎 Advanced Search")
    
    st.sidebar.markdown("---")
    total = len(data['papers']) + len(data['additional_sources'])
    st.sidebar.markdown(f"**📊 {total}+ NASA Data Sources**")

if __name__ == "__main__":
    main()

