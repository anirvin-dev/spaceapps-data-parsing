#!/usr/bin/env python3
"""
NASA Bioscience Summarizer - Knowledge Graph Dashboard
======================================================

Enhanced dashboard with interactive knowledge graphs visualizing relationships
between claims, knowledge gaps, mission insights, topics, and papers.

Usage:
    streamlit run dashboard_knowledge_graph.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from collections import Counter, defaultdict
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Tuple

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

def create_knowledge_graph(data: Dict) -> nx.Graph:
    """Create a network graph from all data sources."""
    G = nx.Graph()
    
    # Add claims nodes
    claims = data['claims'].get('claims', {})
    for claim_id, claim_data in claims.items():
        G.add_node(
            f"claim_{claim_id}",
            type="claim",
            label=claim_data['claim'][:50] + "...",
            full_label=claim_data['claim'],
            score=claim_data['consensus_score'],
            supporting=claim_data['supporting_papers'],
            size=30 + claim_data['consensus_score'] / 3
        )
    
    # Add topics nodes
    topics = data['topics'].get('topics', [])
    for topic in topics:
        topic_id = f"topic_{topic['topic_id']}"
        G.add_node(
            topic_id,
            type="topic",
            label=topic['name'][:40] + "...",
            full_label=topic['name'],
            papers=topic['paper_count'],
            size=40 + topic['paper_count'] / 2
        )
    
    # Add knowledge gaps nodes
    gaps = data['knowledge_gaps'].get('gaps', [])
    for idx, gap in enumerate(gaps):
        gap_id = f"gap_{idx}"
        G.add_node(
            gap_id,
            type="gap",
            label=f"Gap: {', '.join(gap['keywords'][:3])}",
            full_label=', '.join(gap['keywords']),
            score=gap['gap_score'],
            relevance=gap['mission_relevance'],
            size=25 + gap['gap_score'] * 30
        )
    
    # Add mission insights nodes
    insights = data['mission_insights'].get('insights', [])
    for idx, insight in enumerate(insights):
        insight_id = f"insight_{idx}"
        G.add_node(
            insight_id,
            type="insight",
            label=insight['title'][:40] + "...",
            full_label=insight['title'],
            category=insight['category'],
            risk=insight['risk_level'],
            confidence=insight['confidence'],
            size=25 + insight['confidence'] / 3
        )
    
    # Create edges between related nodes
    
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
            # Check overlap
            if any(kw in ' '.join(topic_words) or any(tw in kw for tw in topic_words) for kw in gap_keywords):
                G.add_edge(
                    f"gap_{gap_idx}",
                    f"topic_{topic['topic_id']}",
                    weight=2,
                    relation="identifies_gap_in"
                )
    
    # Connect gaps to insights by category/keyword matching
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

def plot_knowledge_graph(G: nx.Graph, node_filter: str = "all") -> go.Figure:
    """Create an interactive plotly visualization of the knowledge graph."""
    
    # Filter nodes if needed
    if node_filter != "all":
        nodes_to_keep = [n for n, d in G.nodes(data=True) if d['type'] == node_filter or node_filter == "all"]
        # Also keep connected nodes
        extended_nodes = set(nodes_to_keep)
        for node in nodes_to_keep:
            extended_nodes.update(G.neighbors(node))
        G_filtered = G.subgraph(extended_nodes)
    else:
        G_filtered = G
    
    # Use spring layout for positioning
    pos = nx.spring_layout(G_filtered, k=2, iterations=50, seed=42)
    
    # Create edge traces
    edge_traces = []
    for edge in G_filtered.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create node traces by type
    node_types = {
        'claim': {'color': '#FF6B6B', 'symbol': 'circle', 'name': 'Claims'},
        'topic': {'color': '#4ECDC4', 'symbol': 'diamond', 'name': 'Topics'},
        'gap': {'color': '#FFE66D', 'symbol': 'square', 'name': 'Knowledge Gaps'},
        'insight': {'color': '#95E1D3', 'symbol': 'star', 'name': 'Mission Insights'}
    }
    
    node_traces = []
    for node_type, style in node_types.items():
        nodes_of_type = [n for n, d in G_filtered.nodes(data=True) if d['type'] == node_type]
        if not nodes_of_type:
            continue
        
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in nodes_of_type:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            data = G_filtered.nodes[node]
            hover_text = f"<b>{data.get('full_label', data.get('label', node))}</b><br>"
            
            if node_type == 'claim':
                hover_text += f"Consensus: {data.get('score', 0)}%<br>"
                hover_text += f"Supporting Papers: {data.get('supporting', 0)}"
            elif node_type == 'topic':
                hover_text += f"Papers: {data.get('papers', 0)}"
            elif node_type == 'gap':
                hover_text += f"Gap Score: {data.get('score', 0):.2f}<br>"
                hover_text += f"Mission Relevance: {data.get('relevance', 0):.2f}"
            elif node_type == 'insight':
                hover_text += f"Category: {data.get('category', 'N/A')}<br>"
                hover_text += f"Risk: {data.get('risk', 'N/A')}<br>"
                hover_text += f"Confidence: {data.get('confidence', 0):.1f}%"
            
            node_text.append(hover_text)
            node_size.append(data.get('size', 20))
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[G_filtered.nodes[n]['label'] for n in nodes_of_type],
            textposition="top center",
            textfont=dict(size=8),
            hovertext=node_text,
            name=style['name'],
            marker=dict(
                size=node_size,
                color=style['color'],
                symbol=style['symbol'],
                line=dict(width=2, color='white')
            )
        )
        node_traces.append(node_trace)
    
    # Create figure
    fig = go.Figure(data=edge_traces + node_traces)
    
    fig.update_layout(
        title=dict(
            text="NASA Bioscience Knowledge Graph",
            font=dict(size=24, color='#2C3E50')
        ),
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240,240,245,0.5)',
        height=800,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="Black",
            borderwidth=1
        )
    )
    
    return fig

def create_category_network(data: Dict) -> go.Figure:
    """Create a category-level network showing high-level relationships."""
    G = nx.Graph()
    
    # Aggregate by categories
    insights = data['mission_insights'].get('insights', [])
    category_counts = Counter(i['category'] for i in insights)
    
    # Add category nodes
    for category, count in category_counts.items():
        G.add_node(category, type='category', count=count, size=20 + count * 3)
    
    # Add risk level analysis
    risk_categories = defaultdict(list)
    for insight in insights:
        risk_categories[insight['risk_level']].append(insight['category'])
    
    for risk, categories in risk_categories.items():
        risk_node = f"risk_{risk}"
        G.add_node(risk_node, type='risk', risk_level=risk, size=30)
        for cat in set(categories):
            if cat in G.nodes:
                G.add_edge(risk_node, cat, weight=categories.count(cat))
    
    # Layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Create traces
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2].get('weight', 1)
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=weight * 0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Category nodes
    cat_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'category']
    cat_x = [pos[n][0] for n in cat_nodes]
    cat_y = [pos[n][1] for n in cat_nodes]
    cat_size = [G.nodes[n]['size'] for n in cat_nodes]
    cat_text = [f"<b>{n}</b><br>Insights: {G.nodes[n]['count']}" for n in cat_nodes]
    
    cat_trace = go.Scatter(
        x=cat_x, y=cat_y,
        mode='markers+text',
        text=cat_nodes,
        textposition="top center",
        hovertext=cat_text,
        hoverinfo='text',
        name='Categories',
        marker=dict(size=cat_size, color='#3498DB', symbol='circle', line=dict(width=2, color='white'))
    )
    
    # Risk nodes
    risk_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'risk']
    risk_colors = {'high': '#E74C3C', 'medium': '#F39C12', 'low': '#2ECC71'}
    risk_x = [pos[n][0] for n in risk_nodes]
    risk_y = [pos[n][1] for n in risk_nodes]
    risk_size = [G.nodes[n]['size'] for n in risk_nodes]
    risk_color = [risk_colors.get(G.nodes[n]['risk_level'], '#888') for n in risk_nodes]
    risk_text = [f"<b>{G.nodes[n]['risk_level'].upper()} Risk</b>" for n in risk_nodes]
    risk_labels = [G.nodes[n]['risk_level'].upper() for n in risk_nodes]
    
    risk_trace = go.Scatter(
        x=risk_x, y=risk_y,
        mode='markers+text',
        text=risk_labels,
        textposition="bottom center",
        hovertext=risk_text,
        hoverinfo='text',
        name='Risk Levels',
        marker=dict(size=risk_size, color=risk_color, symbol='square', line=dict(width=2, color='white'))
    )
    
    fig = go.Figure(data=edge_traces + [cat_trace, risk_trace])
    
    fig.update_layout(
        title="Mission Insights by Category & Risk Level",
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240,240,245,0.5)',
        height=600
    )
    
    return fig

def create_topic_paper_network(data: Dict, selected_topic_id: int = None) -> go.Figure:
    """Create a network showing topics and their papers."""
    G = nx.Graph()
    
    topics = data['topics'].get('topics', [])
    
    if selected_topic_id is not None:
        topics = [t for t in topics if t['topic_id'] == selected_topic_id]
    
    for topic in topics[:5]:  # Limit to 5 topics for readability
        topic_id = f"topic_{topic['topic_id']}"
        G.add_node(topic_id, type='topic', label=topic['name'], size=50)
        
        # Add top papers
        for paper in topic.get('papers_with_titles', [])[:10]:  # Top 10 papers per topic
            paper_id = f"paper_{paper['id']}"
            if paper_id not in G.nodes:
                G.add_node(paper_id, type='paper', label=paper['title'][:40] + "...", 
                          full_title=paper['title'], size=15)
            G.add_edge(topic_id, paper_id, weight=1)
    
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Edges
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines', line=dict(width=0.3, color='#CCC'),
            hoverinfo='none', showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Topic nodes
    topic_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'topic']
    topic_trace = go.Scatter(
        x=[pos[n][0] for n in topic_nodes],
        y=[pos[n][1] for n in topic_nodes],
        mode='markers+text',
        text=[G.nodes[n]['label'][:30] for n in topic_nodes],
        textposition="top center",
        hovertext=[f"<b>{G.nodes[n]['label']}</b>" for n in topic_nodes],
        hoverinfo='text',
        name='Topics',
        marker=dict(size=[G.nodes[n]['size'] for n in topic_nodes], 
                   color='#9B59B6', symbol='diamond', 
                   line=dict(width=2, color='white'))
    )
    
    # Paper nodes
    paper_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'paper']
    paper_trace = go.Scatter(
        x=[pos[n][0] for n in paper_nodes],
        y=[pos[n][1] for n in paper_nodes],
        mode='markers',
        hovertext=[f"<b>{G.nodes[n]['full_title']}</b>" for n in paper_nodes],
        hoverinfo='text',
        name='Papers',
        marker=dict(size=[G.nodes[n]['size'] for n in paper_nodes], 
                   color='#1ABC9C', symbol='circle',
                   line=dict(width=1, color='white'))
    )
    
    fig = go.Figure(data=edge_traces + [topic_trace, paper_trace])
    
    fig.update_layout(
        title="Topics & Papers Network",
        showlegend=True,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(240,240,245,0.5)',
        height=600
    )
    
    return fig

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

def show_knowledge_graph_page(data):
    """Display interactive knowledge graph."""
    st.header("🕸️ Knowledge Graph Visualization")
    
    st.markdown("""
    Explore the interconnected relationships between scientific claims, research topics, 
    knowledge gaps, and mission insights from 600+ NASA papers.
    """)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Full Network", "Category View", "Topic-Paper Network"])
    
    with tab1:
        st.subheader("Complete Knowledge Network")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            node_filter = st.selectbox(
                "Filter by type:",
                ["all", "claim", "topic", "gap", "insight"],
                format_func=lambda x: {
                    "all": "All Nodes",
                    "claim": "Claims Only",
                    "topic": "Topics Only",
                    "gap": "Knowledge Gaps Only",
                    "insight": "Mission Insights Only"
                }[x]
            )
        
        with st.spinner("Generating knowledge graph..."):
            G = create_knowledge_graph(data)
            st.info(f"📊 Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} connections")
            fig = plot_knowledge_graph(G, node_filter)
            st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        st.subheader("📈 Network Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            claims_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'claim'])
            st.metric("Claims", claims_count)
        with col2:
            topics_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'topic'])
            st.metric("Topics", topics_count)
        with col3:
            gaps_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'gap'])
            st.metric("Knowledge Gaps", gaps_count)
        with col4:
            insights_count = len([n for n, d in G.nodes(data=True) if d['type'] == 'insight'])
            st.metric("Mission Insights", insights_count)
    
    with tab2:
        st.subheader("Mission Insights by Category")
        fig_cat = create_category_network(data)
        st.plotly_chart(fig_cat, use_container_width=True)
        
        st.markdown("""
        **Understanding the Network:**
        - 🔵 **Blue circles** represent research categories
        - 🔴 **Red squares** indicate HIGH risk areas
        - 🟠 **Orange squares** indicate MEDIUM risk areas
        - 🟢 **Green squares** indicate LOW risk areas
        - **Line thickness** shows the strength of connection
        """)
    
    with tab3:
        st.subheader("Topics and Papers Network")
        
        topics = data['topics'].get('topics', [])
        if topics:
            selected_topic = st.selectbox(
                "Focus on specific topic:",
                ["All Topics (showing top 5)"] + [f"{t['topic_id']}: {t['name']}" for t in topics]
            )
            
            topic_id = None
            if selected_topic != "All Topics (showing top 5)":
                topic_id = int(selected_topic.split(":")[0])
            
            fig_topics = create_topic_paper_network(data, topic_id)
            st.plotly_chart(fig_topics, use_container_width=True)
        else:
            st.warning("No topics data available")

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
        page_title="NASA Bioscience Knowledge Graph",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 NASA Bioscience Research Explorer")
    st.markdown("**AI-Powered Knowledge Graph & Analysis Dashboard**")
    
    data = load_dashboard_data()
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Knowledge Graph", "Consensus Claims", "Knowledge Gaps", "Mission Insights"]
    )
    
    if page == "Overview":
        show_overview_page(data)
    elif page == "Knowledge Graph":
        show_knowledge_graph_page(data)
    elif page == "Consensus Claims":
        show_consensus_page(data)
    elif page == "Knowledge Gaps":
        show_knowledge_gaps_page(data)
    elif page == "Mission Insights":
        show_mission_insights_page(data)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Features:**")
    st.sidebar.markdown("- 🕸️ Interactive Knowledge Graphs")
    st.sidebar.markdown("- 🤝 Evidence-backed Consensus")
    st.sidebar.markdown("- 🔍 Knowledge Gap Detection")
    st.sidebar.markdown("- 🚀 Mission Recommendations")
    st.sidebar.markdown("- 📊 600+ NASA Papers Analyzed")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Graph Legend:**")
    st.sidebar.markdown("🔴 Claims | 💎 Topics")
    st.sidebar.markdown("🟡 Gaps | ⭐ Insights")

if __name__ == "__main__":
    main()

