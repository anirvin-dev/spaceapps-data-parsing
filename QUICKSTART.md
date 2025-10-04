# 🚀 NASA Bioscience Summarizer - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install scispaCy model
python -m spacy download en_core_sci_sm
```

### 2. Test with 3 Papers (Quick Test)

```bash
python3 nasa_pipeline_all_in_one.py --mode full --sample 3
```

### 3. Launch Dashboard

```bash
python3 nasa_pipeline_all_in_one.py --mode serve
```

## 📊 What You'll Get

After running the pipeline, you'll have:

- **📄 Extracted Text**: Full text from PDFs with structured sections
- **📝 Summaries**: Both extractive and abstractive summaries
- **🧬 Entities**: Scientific entities (genes, proteins, processes)
- **🎯 Topics**: Research themes and clusters
- **🔍 Search**: Semantic search capabilities
- **📊 Dashboard**: Interactive exploration interface

## 🎯 Key Features

- **Hybrid Summarization**: Combines extractive + abstractive methods
- **Scientific NLP**: Uses scispaCy for biomedical entity recognition
- **Topic Modeling**: BERTopic clustering for research themes
- **Semantic Search**: FAISS-based similarity search
- **Interactive Dashboard**: Streamlit-based exploration

## 📁 Output Structure

```
papers/              # Downloaded PDFs
paper_text/          # Extracted text files
summaries/           # Extractive & abstractive summaries
entities/            # Scientific entities
embeddings/          # Embeddings & search index
topics/              # Topic modeling results
```

## 🔧 Troubleshooting

**Memory Issues?**

```bash
python3 nasa_pipeline_all_in_one.py --mode full --sample 3 --no-gpu
```

**Want to try different models?**

```bash
python3 nasa_pipeline_all_in_one.py --mode full --sample 3 --abstractive-model bart --embedding-model mpnet
```

**Need help?**

```bash
python3 nasa_pipeline_all_in_one.py --help
```

## 🌟 Example Commands

```bash
# Process all 607 papers (takes 2-4 hours)
python3 nasa_pipeline_all_in_one.py --mode full

# Process only download + text extraction
python3 nasa_pipeline_all_in_one.py --mode download --sample 10
python3 nasa_pipeline_all_in_one.py --mode extract_text --sample 10

# Process only summarization
python3 nasa_pipeline_all_in_one.py --mode extractive --sample 10
python3 nasa_pipeline_all_in_one.py --mode abstractive --sample 10

# Process only entity extraction
python3 nasa_pipeline_all_in_one.py --mode entities --sample 10

# Process only embeddings and topics
python3 nasa_pipeline_all_in_one.py --mode embed --sample 10
python3 nasa_pipeline_all_in_one.py --mode topic --sample 10
```

## 📈 Expected Results

For 3 papers (quick test):

- **Time**: 5-10 minutes
- **Storage**: ~50MB
- **Topics**: 3-5 research themes
- **Entities**: 100-300 scientific entities

For all 607 papers:

- **Time**: 2-4 hours (with GPU)
- **Storage**: 2-5GB
- **Topics**: 15-30 research themes
- **Entities**: Thousands of scientific entities

---

**Ready to explore NASA bioscience research with AI! 🚀🧬**
