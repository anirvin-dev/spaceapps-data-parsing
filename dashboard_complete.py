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
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import networkx as nx
from typing import Dict, List, Tuple

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

def create_knowledge_graph(data: Dict) -> nx.Graph:
    """Create a network graph from all data sources with improved connections."""
    G = nx.Graph()
    
    # Add claims nodes with smaller base sizes
    claims = data['claims'].get('claims', {})
    for claim_id, claim_data in claims.items():
        G.add_node(
            f"claim_{claim_id}",
            type="claim",
            label=claim_data['claim'][:40] + "..." if len(claim_data['claim']) > 40 else claim_data['claim'],
            full_label=claim_data['claim'],
            score=claim_data['consensus_score'],
            supporting=claim_data['supporting_papers'],
            size=15 + claim_data['consensus_score'] / 5
        )
    
    # Add topics nodes with smaller base sizes
    topics = data['topics'].get('topics', [])
    for topic in topics:
        topic_id = f"topic_{topic['topic_id']}"
        G.add_node(
            topic_id,
            type="topic",
            label=topic['name'][:30] + "..." if len(topic['name']) > 30 else topic['name'],
            full_label=topic['name'],
            papers=topic['paper_count'],
            size=20 + topic['paper_count'] / 4
        )
    
    # Add knowledge gaps nodes with smaller base sizes
    gaps = data['knowledge_gaps'].get('gaps', [])
    for idx, gap in enumerate(gaps):
        gap_id = f"gap_{idx}"
        keywords_text = ', '.join(gap['keywords'][:3])
        G.add_node(
            gap_id,
            type="gap",
            label=keywords_text[:35] + "..." if len(keywords_text) > 35 else keywords_text,
            full_label=', '.join(gap['keywords']),
            score=gap['gap_score'],
            relevance=gap['mission_relevance'],
            size=15 + gap['gap_score'] * 20
        )
    
    # Add mission insights nodes with smaller base sizes
    insights = data['mission_insights'].get('insights', [])
    for idx, insight in enumerate(insights):
        insight_id = f"insight_{idx}"
        G.add_node(
            insight_id,
            type="insight",
            label=insight['title'][:30] + "..." if len(insight['title']) > 30 else insight['title'],
            full_label=insight['title'],
            category=insight['category'],
            risk=insight['risk_level'],
            confidence=insight['confidence'],
            size=15 + insight['confidence'] / 5
        )
    
    # Create edges between related nodes (improved matching)
    
    # Connect claims to topics by category matching
    for claim_id, claim_data in claims.items():
        claim_text = claim_data['claim'].lower()
        for topic in topics:
            topic_words = [w.lower() for w in topic['top_words'][:10]]
            # Check if any topic word appears in claim
            if any(word in claim_text for word in topic_words):
                G.add_edge(
                    f"claim_{claim_id}",
                    f"topic_{topic['topic_id']}",
                    weight=2,
                    relation="related_to"
                )
    
    # Connect insights to topics by category
    category_to_topic = {
        "Musculoskeletal": 1,
        "Radiation": 2,
        "Immunology": 3,
        "Cardiovascular": 4,
        "Molecular Biology": 5,
        "Cellular Biology": 5,
        "Genomics": 5,
        "Life Support": 6,
        "Ophthalmology": 7,
        "Sleep Medicine": 7,
        "Behavioral Health": 7,
        "Nutrition": 8,
        "Microbiology": 9,
        "Regenerative Medicine": 10,
        "Exercise Physiology": 1,
        "Pharmacology": 8,
        "Physiology": 4
    }
    
    for idx, insight in enumerate(insights):
        category = insight['category']
        if category in category_to_topic:
            topic_id = category_to_topic[category]
            if f"topic_{topic_id}" in G.nodes:
                G.add_edge(
                    f"insight_{idx}",
                    f"topic_{topic_id}",
                    weight=3,
                    relation="addresses"
                )
    
    # Connect gaps to topics by keyword matching
    for gap_idx, gap in enumerate(gaps):
        gap_keywords = [k.lower() for k in gap['keywords']]
        for topic in topics:
            topic_words = [w.lower() for w in topic['top_words'][:15]]
            if any(kw in ' '.join(topic_words) or any(tw in kw for tw in topic_words) for kw in gap_keywords):
                G.add_edge(
                    f"gap_{gap_idx}",
                    f"topic_{topic['topic_id']}",
                    weight=2,
                    relation="identifies_gap_in"
                )
    
    # Connect gaps to insights
    for gap_idx, gap in enumerate(gaps):
        gap_keywords = [k.lower() for k in gap['keywords']]
        for insight_idx, insight in enumerate(insights):
            insight_text = (insight['title'] + " " + insight['category']).lower()
            if any(kw in insight_text for kw in gap_keywords):
                G.add_edge(
                    f"gap_{gap_idx}",
                    f"insight_{insight_idx}",
                    weight=2,
                    relation="informs"
                )
    
    return G

def plot_knowledge_graph_improved(G: nx.Graph, node_filter: str = "all") -> go.Figure:
    """Create a smooth, professional interactive plotly visualization."""
    
    # Filter nodes if needed
    if node_filter != "all":
        nodes_to_keep = [n for n, d in G.nodes(data=True) if d['type'] == node_filter]
        extended_nodes = set(nodes_to_keep)
        for node in nodes_to_keep:
            extended_nodes.update(G.neighbors(node))
        G_filtered = G.subgraph(extended_nodes)
    else:
        G_filtered = G
    
    # Excellent spacing to prevent any overlap
    pos = nx.spring_layout(G_filtered, k=5.5, iterations=200, seed=42)
    
    # Create visible, clean connection lines
    edge_traces = []
    for edge in G_filtered.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Simple straight lines - more visible
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=1.5, color='rgba(100,150,255,0.4)'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Simple, clean blue/white theme for Framer embedding
    node_styles = {
        'claim': {
            'color': '#4A90E2',
            'symbol': 'circle',
            'name': '🔴 Claims',
            'line_color': '#FFFFFF'
        },
        'topic': {
            'color': '#0066CC',
            'symbol': 'diamond',
            'name': '💎 Topics',
            'line_color': '#FFFFFF'
        },
        'gap': {
            'color': '#87CEEB',
            'symbol': 'square',
            'name': '🟡 Knowledge Gaps',
            'line_color': '#FFFFFF'
        },
        'insight': {
            'color': '#1E90FF',
            'symbol': 'star',
            'name': '⭐ Mission Insights',
            'line_color': '#FFFFFF'
        }
    }
    
    node_traces = []
    for node_type, style in node_styles.items():
        nodes_of_type = [n for n, d in G_filtered.nodes(data=True) if d['type'] == node_type]
        if not nodes_of_type:
            continue
        
        node_x = []
        node_y = []
        node_text = []
        node_hover = []
        node_size = []
        
        for node in nodes_of_type:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = G_filtered.nodes[node]
            node_text.append(data.get('label', '')[:25])
            
            # Improved hover text
            hover_text = f"<b>{data.get('full_label', data.get('label', node))}</b><br><br>"
            
            if node_type == 'claim':
                hover_text += f"<i>Consensus Score:</i> {data.get('score', 0)}%<br>"
                hover_text += f"<i>Supporting Papers:</i> {data.get('supporting', 0)}"
            elif node_type == 'topic':
                hover_text += f"<i>Papers in Topic:</i> {data.get('papers', 0)}"
            elif node_type == 'gap':
                hover_text += f"<i>Gap Score:</i> {data.get('score', 0):.2f}<br>"
                hover_text += f"<i>Mission Relevance:</i> {data.get('relevance', 0):.0%}"
            elif node_type == 'insight':
                hover_text += f"<i>Category:</i> {data.get('category', 'N/A')}<br>"
                hover_text += f"<i>Risk Level:</i> {data.get('risk', 'N/A').upper()}<br>"
                hover_text += f"<i>Confidence:</i> {data.get('confidence', 0):.1f}%"
            
            node_hover.append(hover_text)
            # Make nodes smaller (reduce size by 40%)
            node_size.append(data.get('size', 20) * 0.6)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=9, family="Arial, sans-serif", color="white"),
            hovertext=node_hover,
            name=style['name'],
            marker=dict(
                size=node_size,
                color=style['color'],
                symbol=style['symbol'],
                line=dict(width=3, color=style['line_color']),
                opacity=1.0
            )
        )
        node_traces.append(node_trace)
    
    # Create figure with clean dark blue theme (perfect for Framer embedding)
    fig = go.Figure(data=edge_traces + node_traces)
    
    fig.update_layout(
        title=dict(
            text="<b>NASA Bioscience Knowledge Graph</b>",
            font=dict(size=24, color='#FFFFFF', family="Arial, sans-serif"),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=60),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#1a1f2e',
        paper_bgcolor='#0f1419',
        height=900,
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(26,31,46,0.95)",
            bordercolor="#FFFFFF",
            borderwidth=2,
            font=dict(size=11, family="Arial, sans-serif", color="white")
        )
    )
    
    return fig

def show_knowledge_graph_page(data):
    """Display interactive knowledge graph - NEW TAB!"""
    st.header("🕸️ Knowledge Graph Visualization")
    
    st.markdown("""
    <div style='background-color: #E8F4F8; padding: 15px; border-radius: 10px; border-left: 5px solid #4ECDC4;'>
    <p style='margin: 0; color: #2C3E50;'>
    Explore the interconnected relationships between <b>scientific claims</b>, <b>research topics</b>, 
    <b>knowledge gaps</b>, and <b>mission insights</b> from <b>600+ NASA papers and 1500+ additional sources</b>.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")  # Spacing
    
    # Check if we have the necessary data
    has_claims = len(data['claims'].get('claims', {})) > 0
    has_gaps = len(data['knowledge_gaps'].get('gaps', [])) > 0
    has_insights = len(data['mission_insights'].get('insights', [])) > 0
    has_topics = len(data['topics'].get('topics', [])) > 0
    
    if not all([has_claims, has_gaps, has_insights, has_topics]):
        st.warning("⚠️ Some analysis data is missing. For best results, ensure all analysis files are generated.")
        st.info("Run: `python3 create_demo_analysis.py` to generate sample data.")
    
    # Filter controls in a nice layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        node_filter = st.selectbox(
            "🔍 Filter Network View:",
            ["all", "claim", "topic", "gap", "insight"],
            format_func=lambda x: {
                "all": "🌐 All Connections (Full Network)",
                "claim": "🔴 Claims & Related Nodes",
                "topic": "💎 Topics & Related Nodes",
                "gap": "🟡 Knowledge Gaps & Related Nodes",
                "insight": "⭐ Mission Insights & Related Nodes"
            }[x]
        )
    
    with col2:
        st.metric("Total Nodes", "62+", help="Claims + Topics + Gaps + Insights")
    
    with col3:
        st.metric("Connections", "~100", help="Automatically discovered relationships")
    
    st.write("")  # Spacing
    
    # Generate graph
    with st.spinner("🎨 Generating knowledge graph..."):
        try:
            G = create_knowledge_graph(data)
            fig = plot_knowledge_graph_improved(G, node_filter)
            st.plotly_chart(fig, use_container_width=True)
            
            # Network statistics
            st.subheader("📊 Network Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                claims_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'claim'])
                st.metric("🔴 Claims", claims_count)
            
            with col2:
                topics_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'topic'])
                st.metric("💎 Topics", topics_count)
            
            with col3:
                gaps_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'gap'])
                st.metric("🟡 Gaps", gaps_count)
            
            with col4:
                insights_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'insight'])
                st.metric("⭐ Insights", insights_count)
            
            # Interactive guide
            with st.expander("ℹ️ How to Use This Graph"):
                st.markdown("""
                **Interacting with the Graph:**
                - 🖱️ **Hover** over nodes to see detailed information
                - 🔍 **Zoom** using scroll wheel or pinch gesture
                - ↔️ **Pan** by clicking and dragging
                - 🎯 **Click** legend items to show/hide node types
                
                **Understanding the Visualization:**
                - **Node Size** = Importance (larger = more significant)
                - **Lines** = Discovered relationships between concepts
                - **Colors** = Different data types (see legend)
                - **Clustering** = Related concepts are positioned closer together
                """)
            
        except Exception as e:
            st.error(f"Error generating knowledge graph: {str(e)}")
            st.info("This feature requires analysis data. Run the analysis pipeline first.")

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
         "Consensus Claims", "Knowledge Gaps", "Mission Insights", "Additional NASA Sources",
         "🕸️ Knowledge Graph"]
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
    elif page == "🕸️ Knowledge Graph":
        show_knowledge_graph_page(data)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**✨ Features:**")
    st.sidebar.markdown("- 📄 Paper Summaries (Extract + Abstract)")
    st.sidebar.markdown("- 🤝 Evidence-backed Consensus")
    st.sidebar.markdown("- 🔍 Knowledge Gap Detection")
    st.sidebar.markdown("- 🚀 Mission Recommendations")
    st.sidebar.markdown("- 🌐 Multi-Source Integration")
    st.sidebar.markdown("- 🏷️ Topic Clustering")
    st.sidebar.markdown("- 🔎 Advanced Search")
    st.sidebar.markdown("- 🕸️ **NEW!** Knowledge Graph")
    
    st.sidebar.markdown("---")
    total = len(data['papers']) + len(data['additional_sources'])
    st.sidebar.markdown(f"**📊 {total}+ NASA Data Sources**")

if __name__ == "__main__":
    main()

