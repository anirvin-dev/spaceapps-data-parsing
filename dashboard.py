"""
NASA Bioscience Dashboard - Interactive Exploration Interface
============================================================

A comprehensive Streamlit dashboard for exploring NASA bioscience research papers.
Features:
- Paper search and filtering
- Topic clustering visualization
- Entity extraction analysis
- Semantic similarity search
- Interactive plots and charts
- Export capabilities

Usage:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from wordcloud import WordCloud
import io
import base64
from collections import Counter, defaultdict
import re

# Page configuration
st.set_page_config(
    page_title="NASA Bioscience Explorer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .paper-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
    .entity-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Data loading functions
@st.cache_data
def load_papers_data():
    """Load paper metadata and processing results."""
    data = {
        'papers': [],
        'summaries': {},
        'entities': {},
        'topics': {},
        'embeddings': None
    }
    
    # Load paper metadata
    papers_csv = Path("data/nasa_papers.csv")
    if papers_csv.exists():
        df = pd.read_csv(papers_csv)
        data['papers'] = df.to_dict('records')
    
    # Load summaries
    summaries_dir = Path("summaries")
    if summaries_dir.exists():
        for summary_file in summaries_dir.rglob("*_extractive.txt"):
            doc_id = summary_file.stem.replace("_extractive", "")
            data['summaries'][doc_id] = summary_file.read_text()
        
        for summary_file in summaries_dir.rglob("*_abstractive.json"):
            doc_id = summary_file.stem.replace("_abstractive", "")
            try:
                data['summaries'][doc_id + "_abstractive"] = json.loads(summary_file.read_text())
            except:
                pass
    
    # Load entities
    entities_dir = Path("entities")
    if entities_dir.exists():
        for entity_file in entities_dir.rglob("*_entities.json"):
            doc_id = entity_file.stem.replace("_entities", "")
            try:
                data['entities'][doc_id] = json.loads(entity_file.read_text())
            except:
                pass
    
    # Load topics
    topics_file = Path("topics/topics.json")
    if topics_file.exists():
        try:
            data['topics'] = json.loads(topics_file.read_text())
        except:
            pass
    
    return data

@st.cache_data
def load_embeddings():
    """Load FAISS embeddings and document info."""
    try:
        index = faiss.read_index("embeddings/faiss.index")
        with open("embeddings/docs.json", "r") as f:
            docs = json.load(f)
        return index, docs
    except:
        return None, None

def create_wordcloud(text, title="Word Cloud"):
    """Create a word cloud from text."""
    if not text:
        return None
    
    # Clean text
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    
    if len(words) < 10:
        return None
    
    # Create word cloud
    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        max_words=100,
        colormap='viridis'
    ).generate(' '.join(words))
    
    return wordcloud

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 NASA Bioscience Explorer</h1>', unsafe_allow_html=True)
    st.markdown("**Explore NASA bioscience research papers with AI-powered analysis**")
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_papers_data()
        embeddings_index, embeddings_docs = load_embeddings()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Overview", "Paper Search", "Topic Analysis", "Entity Explorer", "Similarity Search", "Export Data"]
    )
    
    if page == "Overview":
        show_overview(data)
    elif page == "Paper Search":
        show_paper_search(data)
    elif page == "Topic Analysis":
        show_topic_analysis(data)
    elif page == "Entity Explorer":
        show_entity_explorer(data)
    elif page == "Similarity Search":
        show_similarity_search(data, embeddings_index, embeddings_docs)
    elif page == "Export Data":
        show_export_data(data)

def show_overview(data):
    """Show overview dashboard with key metrics."""
    st.header("📊 Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Papers", len(data['papers']))
    
    with col2:
        st.metric("Processed Summaries", len(data['summaries']))
    
    with col3:
        st.metric("Entity Extractions", len(data['entities']))
    
    with col4:
        st.metric("Topics Identified", len(data['topics']))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Papers by Processing Status")
        if data['papers']:
            df = pd.DataFrame(data['papers'])
            status_counts = {
                'Total Papers': len(df),
                'With Summaries': len(data['summaries']),
                'With Entities': len(data['entities'])
            }
            
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Processing Status"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Entity Types Distribution")
        if data['entities']:
            all_entities = []
            for entities in data['entities'].values():
                if isinstance(entities, list):
                    all_entities.extend(entities)
            
            if all_entities:
                entity_types = [e.get('label', 'UNKNOWN') for e in all_entities if isinstance(e, dict)]
                type_counts = Counter(entity_types)
                
                fig = px.bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    title="Entity Types",
                    labels={'x': 'Entity Type', 'y': 'Count'}
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

def show_paper_search(data):
    """Show paper search and exploration interface."""
    st.header("🔍 Paper Search & Exploration")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search papers:", placeholder="Enter keywords, paper titles, or topics...")
    
    with col2:
        search_type = st.selectbox("Search in:", ["Title", "Summary", "All"])
    
    # Filter papers
    filtered_papers = data['papers']
    if search_query:
        query_lower = search_query.lower()
        filtered_papers = [
            paper for paper in data['papers']
            if query_lower in str(paper.get('title', '')).lower() or
               (search_type in ["Summary", "All"] and 
                query_lower in str(data['summaries'].get(paper.get('id', ''), '')).lower())
        ]
    
    st.write(f"Found {len(filtered_papers)} papers")
    
    # Display papers
    for i, paper in enumerate(filtered_papers[:20]):  # Limit to 20 for performance
        with st.expander(f"📄 {paper.get('title', 'Untitled')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**ID:** {paper.get('id', 'N/A')}")
                st.write(f"**Link:** {paper.get('link', 'N/A')}")
                
                # Show summary if available
                paper_id = str(paper.get('id', ''))
                if paper_id in data['summaries']:
                    st.write("**Extractive Summary:**")
                    st.write(data['summaries'][paper_id][:500] + "..." if len(data['summaries'][paper_id]) > 500 else data['summaries'][paper_id])
                
                # Show abstractive summary if available
                abstractive_key = paper_id + "_abstractive"
                if abstractive_key in data['summaries']:
                    abstractive_summary = data['summaries'][abstractive_key]
                    if isinstance(abstractive_summary, dict) and 'final_summary' in abstractive_summary:
                        st.write("**Abstractive Summary:**")
                        st.write(abstractive_summary['final_summary'][:500] + "..." if len(abstractive_summary['final_summary']) > 500 else abstractive_summary['final_summary'])
            
            with col2:
                # Show entities if available
                if paper_id in data['entities']:
                    st.write("**Key Entities:**")
                    entities = data['entities'][paper_id]
                    if isinstance(entities, list):
                        for entity in entities[:5]:  # Show top 5
                            if isinstance(entity, dict):
                                st.markdown(f'<span class="entity-tag">{entity.get("text", "")} ({entity.get("label", "")})</span>', unsafe_allow_html=True)

def show_topic_analysis(data):
    """Show topic modeling analysis."""
    st.header("🎯 Topic Analysis")
    
    if not data['topics']:
        st.warning("No topic analysis data available. Run the pipeline first.")
        return
    
    # Topic distribution
    st.subheader("Topic Distribution")
    
    # Create topic visualization
    topics = data['topics']
    if isinstance(topics, dict) and 'topic_info' in topics:
        topic_info = topics['topic_info']
        df_topics = pd.DataFrame(topic_info)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_topics.head(10),
                x='Count',
                y='Name',
                orientation='h',
                title="Top 10 Topics by Paper Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Word cloud for most common topic
            if len(df_topics) > 0:
                st.write("**Most Common Topic Words:**")
                # This would need topic words data
                st.info("Topic words visualization would go here")
    
    # Topic exploration
    st.subheader("Explore Topics")
    if isinstance(topics, dict) and 'doc_topics' in topics:
        topic_mapping = topics['doc_topics']
        selected_topic = st.selectbox("Select a topic:", list(topic_mapping.keys())[:10])
        
        if selected_topic in topic_mapping:
            papers_in_topic = topic_mapping[selected_topic]
            st.write(f"Papers in topic '{selected_topic}': {len(papers_in_topic)}")
            
            for paper_id in papers_in_topic[:5]:  # Show first 5
                paper = next((p for p in data['papers'] if str(p.get('id', '')) == paper_id), None)
                if paper:
                    st.write(f"- {paper.get('title', 'Untitled')}")

def show_entity_explorer(data):
    """Show entity extraction analysis."""
    st.header("🧬 Entity Explorer")
    
    if not data['entities']:
        st.warning("No entity data available. Run the pipeline first.")
        return
    
    # Entity statistics
    all_entities = []
    for entities in data['entities'].values():
        if isinstance(entities, list):
            all_entities.extend(entities)
    
    if not all_entities:
        st.warning("No entities found.")
        return
    
    # Entity type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entity Type Distribution")
        entity_types = [e.get('label', 'UNKNOWN') for e in all_entities if isinstance(e, dict)]
        type_counts = Counter(entity_types)
        
        fig = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            title="Entity Types"
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
    
    # Entity search
    st.subheader("Search Entities")
    entity_search = st.text_input("Search for specific entities:")
    
    if entity_search:
        matching_entities = [
            e for e in all_entities
            if isinstance(e, dict) and entity_search.lower() in e.get('text', '').lower()
        ]
        
        if matching_entities:
            st.write(f"Found {len(matching_entities)} matching entities:")
            for entity in matching_entities[:20]:
                st.markdown(f'<span class="entity-tag">{entity.get("text", "")} ({entity.get("label", "")})</span>', unsafe_allow_html=True)
        else:
            st.info("No matching entities found.")

def show_similarity_search(data, embeddings_index, embeddings_docs):
    """Show semantic similarity search."""
    st.header("🔗 Semantic Similarity Search")
    
    if embeddings_index is None or embeddings_docs is None:
        st.warning("No embeddings available. Run the pipeline first.")
        return
    
    # Search interface
    search_text = st.text_area("Enter text to find similar papers:", height=100)
    
    if search_text and st.button("Find Similar Papers"):
        try:
            # Load embedding model
            model = SentenceTransformer("allenai-specter")
            query_embedding = model.encode([search_text])
            
            # Search FAISS index
            k = 10
            distances, indices = embeddings_index.search(query_embedding, k)
            
            st.write("**Most Similar Papers:**")
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(embeddings_docs):
                    doc = embeddings_docs[idx]
                    similarity_score = 1 - distance  # Convert distance to similarity
                    
                    with st.expander(f"#{i+1} Similarity: {similarity_score:.3f} - {doc.get('id', 'Unknown')}"):
                        st.write(f"**ID:** {doc.get('id', 'N/A')}")
                        st.write(f"**Summary:** {doc.get('text', 'N/A')[:300]}...")
                        
                        # Show link to original paper
                        paper = next((p for p in data['papers'] if str(p.get('id', '')) == doc.get('id', '')), None)
                        if paper:
                            st.write(f"**Title:** {paper.get('title', 'N/A')}")
                            st.write(f"**Link:** {paper.get('link', 'N/A')}")
        
        except Exception as e:
            st.error(f"Search failed: {e}")

def show_export_data(data):
    """Show data export options."""
    st.header("📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Options")
        
        export_format = st.selectbox("Export format:", ["CSV", "JSON", "TXT"])
        
        if st.button("Export Paper Metadata"):
            if data['papers']:
                df = pd.DataFrame(data['papers'])
                if export_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="nasa_papers_metadata.csv",
                        mime="text/csv"
                    )
                elif export_format == "JSON":
                    json_data = df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name="nasa_papers_metadata.json",
                        mime="application/json"
                    )
    
    with col2:
        st.subheader("Export Summaries")
        
        if st.button("Export All Summaries"):
            if data['summaries']:
                summaries_text = ""
                for doc_id, summary in data['summaries'].items():
                    if isinstance(summary, str):  # Extractive summaries
                        summaries_text += f"\n=== Document {doc_id} ===\n{summary}\n"
                
                st.download_button(
                    label="Download Summaries",
                    data=summaries_text,
                    file_name="nasa_paper_summaries.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
