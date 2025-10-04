# 🚀 NASA Bioscience Summarizer

A comprehensive AI-powered system for processing and analyzing NASA bioscience research publications. This system downloads, processes, and analyzes 608 NASA bioscience research papers using state-of-the-art natural language processing techniques.

## 🌟 Features

- **PDF Download & Processing**: Automated download and text extraction from scientific papers
- **Hybrid Summarization**: Both extractive (LexRank) and abstractive (LED/PRIMERA/BigBird) summaries
- **Scientific Entity Extraction**: Using scispaCy for biomedical entity recognition
- **Topic Modeling**: BERTopic clustering to identify research themes
- **Semantic Search**: FAISS-based similarity search for finding related papers
- **Interactive Dashboard**: Streamlit-based exploration interface
- **Export Capabilities**: Export summaries, entities, and analysis results

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- 8GB+ RAM recommended
- GPU optional but recommended for faster processing

### Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd spaceapps-data-parsing
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Install scispaCy model:**

```bash
python -m spacy download en_core_sci_sm
```

## 📊 Data Structure

The system expects a CSV file at `data/nasa_papers.csv` with the following columns:

- `id`: Unique identifier for the paper
- `title`: Paper title
- `link`: URL to the paper (PDF or webpage)

Example:

```csv
id,title,link
1,"Mice in Bion-M 1 space mission: training and selection",https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/
2,"Microgravity induces pelvic bone loss through osteoclastic activity",https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/
```

## 🚀 Usage

### Quick Start (Test with 3 papers)

```bash
python nasa_pipeline_all_in_one.py --mode full --sample 3
```

### Complete Pipeline (All papers)

```bash
python nasa_pipeline_all_in_one.py --mode full
```

### Individual Pipeline Stages

```bash
# Download papers only
python nasa_pipeline_all_in_one.py --mode download --sample 10

# Extract text from PDFs
python nasa_pipeline_all_in_one.py --mode extract_text --sample 10

# Create extractive summaries
python nasa_pipeline_all_in_one.py --mode extractive --sample 10

# Create abstractive summaries
python nasa_pipeline_all_in_one.py --mode abstractive --sample 10

# Extract scientific entities
python nasa_pipeline_all_in_one.py --mode entities --sample 10

# Compute embeddings and create search index
python nasa_pipeline_all_in_one.py --mode embed --sample 10

# Perform topic clustering
python nasa_pipeline_all_in_one.py --mode topic --sample 10
```

### Launch Interactive Dashboard

```bash
python nasa_pipeline_all_in_one.py --mode serve
# or
streamlit run dashboard.py
```

### Advanced Options

```bash
# Use different models
python nasa_pipeline_all_in_one.py --mode full --abstractive-model led --embedding-model specter

# Force CPU mode
python nasa_pipeline_all_in_one.py --mode full --no-gpu

# Verbose logging
python nasa_pipeline_all_in_one.py --mode full --verbose
```

## 🤖 Available Models

### Abstractive Summarization Models

- `led`: LED (Longformer Encoder-Decoder) - Best for long documents
- `primera`: PRIMERA - Multi-document summarization
- `bigbird`: BigBird PEGASUS - Biomedical focus
- `bart`: BART - General purpose

### Embedding Models

- `specter`: SPECTER - Scientific papers (recommended)
- `scibert`: SciBERT - Scientific domain
- `mpnet`: MPNet - General purpose
- `biobert`: BioBERT - Biomedical focus

### Entity Extraction Models

- `sm`: Small scispaCy model (fast)
- `md`: Medium scispaCy model (balanced)
- `lg`: Large scispaCy model (most accurate)

## 📁 Output Structure

The pipeline creates the following directory structure:

```
spaceapps-data-parsing/
├── data/
│   └── nasa_papers.csv          # Input CSV file
├── papers/                      # Downloaded PDFs
├── paper_text/                  # Extracted text files
│   ├── *.txt                   # Full text
│   └── *_sections.txt          # Structured sections
├── summaries/
│   ├── extractive/             # Extractive summaries
│   └── abstractive/            # Abstractive summaries
├── entities/                    # Scientific entities
├── embeddings/                  # Embeddings and FAISS index
├── topics/                      # Topic modeling results
└── dashboard.py                 # Interactive dashboard
```

## 📊 Dashboard Features

The interactive Streamlit dashboard provides:

- **Overview**: Processing statistics and pipeline status
- **Paper Explorer**: Browse individual papers with summaries and entities
- **Topic Analysis**: Visualize research themes and clusters
- **Entity Explorer**: Analyze scientific entities across papers
- **Search Papers**: Find papers by keywords or similarity
- **Export Data**: Download results in various formats

## 🔧 Configuration

Key configuration parameters in `nasa_pipeline_all_in_one.py`:

```python
# Processing parameters
CHUNK_TOKENS = 8000              # Max tokens per chunk
CHUNK_OVERLAP = 200              # Overlap between chunks
FINAL_SUM_MAXLEN = 300           # Max summary length
NUM_TOPICS = 20                  # Number of topics for clustering
MIN_TOPIC_SIZE = 5               # Minimum documents per topic
```

## 🐛 Troubleshooting

### Common Issues

1. **Memory errors**: Reduce `--sample` size or use `--no-gpu`
2. **Model download fails**: Check internet connection, try different models
3. **PDF extraction fails**: Some PDFs may be image-based or corrupted
4. **scispaCy model not found**: Run `python -m spacy download en_core_sci_sm`

### Performance Tips

- Use GPU for faster processing (if available)
- Start with `--sample 3` to test the pipeline
- Process in stages if memory is limited
- Use smaller models for faster processing

## 📈 Expected Results

For the full dataset of 608 papers:

- **Processing Time**: 2-4 hours (with GPU), 6-12 hours (CPU only)
- **Storage**: ~2-5 GB for all outputs
- **Topics**: 15-30 research themes typically identified
- **Entities**: Thousands of scientific entities extracted
- **Summaries**: Both extractive and abstractive summaries for each paper

## 🤝 Contributing

This project was developed for the NASA Space Apps Hackathon. Contributions are welcome!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NASA for providing the bioscience research dataset
- Hugging Face for transformer models
- AllenAI for SPECTER and scientific models
- The scispaCy team for biomedical NLP tools
- Streamlit for the interactive dashboard framework

## 📞 Support

For questions or issues:

1. Check the troubleshooting section
2. Review the logs in `nasa_pipeline.log`
3. Try with a smaller sample size first
4. Ensure all dependencies are installed correctly

---

**Built for NASA Space Apps Hackathon 2024** 🚀🌍
