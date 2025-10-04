#!/usr/bin/env python3
"""
NASA Bioscience Summarizer - Enhanced Dashboard
===============================================

Enhanced dashboard with Consensus Claims, Knowledge Gaps, and Mission Insights.

Usage:
    streamlit run dashboard_enhanced.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# Configuration
ROOT = Path.cwd()
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
TOPICS_DIR = ROOT / "topics"
ANALYSIS_DIR = ROOT / "analysis"

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
    
    with col1:
        st.metric("Total Papers", len(data['papers']))
    
    with col2:
        st.metric("Summaries", len(data['abstractive_summaries']))
    
    with col3:
        st.metric("Claims", len(data['claims'].get('claims', {})))
    
    with col4:
        st.metric("Mission Insights", len(data['mission_insights'].get('insights', [])))
    
    # Show processing status
    st.subheader("🔄 Pipeline Status")
    total = len(data['papers'])
    if total > 0:
        ext = len(data['extractive_summaries'])
        abs_sum = len(data['abstractive_summaries'])
        st.progress(ext/total, text=f"Extractive: {ext}/{total}")
        st.progress(abs_sum/total, text=f"Abstractive: {abs_sum}/{total}")

def show_consensus_page(data):
    """Display consensus claims with evidence."""
    st.header("🤝 Consensus & Evidence Analysis")
    
    claims = data['claims'].get('claims', {})
    
    if not claims:
        st.warning("No consensus data available. Run: `python3 create_demo_analysis.py`")
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
        st.warning("No gap data. Run: `python3 create_demo_analysis.py`")
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
        st.warning("No insights. Run: `python3 create_demo_analysis.py`")
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

def main():
    """Main app."""
    st.set_page_config(
        page_title="NASA Bioscience Research Explorer",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**AI-Powered Analysis with Consensus & Mission Insights**")
    
    data = load_dashboard_data()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Consensus Claims", "Knowledge Gaps", "Mission Insights"]
    )
    
    if page == "Overview":
        show_overview_page(data)
    elif page == "Consensus Claims":
        show_consensus_page(data)
    elif page == "Knowledge Gaps":
        show_knowledge_gaps_page(data)
    elif page == "Mission Insights":
        show_mission_insights_page(data)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Features:**")
    st.sidebar.markdown("- 🤝 Evidence-backed Consensus")
    st.sidebar.markdown("- 🔍 Knowledge Gap Detection")
    st.sidebar.markdown("- 🚀 Mission Recommendations")
    st.sidebar.markdown("- 📊 608 NASA Papers Analyzed")

if __name__ == "__main__":
    main()

