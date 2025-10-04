# 🚀 Complete User Guide: NASA Bioscience Summarizer

## ✅ **Current Status - ALL ISSUES FIXED!**

- ✅ All dependencies installed and working
- ✅ Import errors resolved
- ✅ Streamlit context issues fixed
- ✅ Pipeline tested and functional
- ✅ Dashboard working properly

---

## 🎯 **How to Run the Program**

### **Step 1: Quick Test (Recommended First)**

```bash
cd /Applications/SpaceAppsHackatho/spaceapps-data-parsing
python3 nasa_pipeline_simple.py --mode full --sample 3 --verbose
```

This will process 3 papers to verify everything works.

### **Step 2: Process Your Full Dataset (607 Papers)**

```bash
python3 nasa_pipeline_simple.py --mode full --verbose
```

This will process all 607 papers from your CSV file.

### **Step 3: Launch Interactive Dashboard**

```bash
# Option 1: Using the pipeline command
python3 nasa_pipeline_simple.py --mode serve

# Option 2: Direct Streamlit command
streamlit run dashboard_simple.py
```

The dashboard will open at: **http://localhost:8501**

---

## 📊 **What the Program Does**

### **Pipeline Stages:**

1. **📥 Download PDFs** - Downloads research papers from your CSV links
2. **📄 Text Extraction** - Extracts and cleans text from PDFs
3. **📝 Extractive Summarization** - Creates summaries by selecting key sentences
4. **🤖 Abstractive Summarization** - Uses AI to generate concise summaries
5. **🔍 Topic Analysis** - Identifies research themes and topics

### **Dashboard Features:**

- **📊 Overview** - Statistics and processing status
- **🔍 Paper Explorer** - Browse individual papers and summaries
- **🔍 Topic Analysis** - Visualize research themes
- **🔎 Search** - Find papers by keywords

---

## 📁 **File Structure Created**

```
spaceapps-data-parsing/
├── data/
│   └── nasa_papers.csv          # Your source data (607 papers)
├── papers/                      # Downloaded PDFs
├── paper_text/                  # Extracted text and sections
├── summaries/
│   ├── extractive/             # Extractive summaries
│   └── abstractive/            # AI-generated summaries
├── topics/                     # Topic analysis results
├── nasa_pipeline_simple.py     # Main pipeline script
└── dashboard_simple.py         # Interactive dashboard
```

---

## 🔧 **Processing Your Additional 500 Sources**

### **Method 1: Add to Existing CSV**

```bash
# If you have a new CSV with 500 sources
python3 -c "
import pandas as pd
# Load existing data
existing = pd.read_csv('data/nasa_papers.csv')
# Load new data (replace 'your_new_500_sources.csv' with your filename)
new_data = pd.read_csv('your_new_500_sources.csv')
# Add IDs starting from 608
new_data.insert(0, 'id', range(608, 608 + len(new_data)))
# Combine datasets
combined = pd.concat([existing, new_data], ignore_index=True)
# Save combined dataset
combined.to_csv('data/nasa_papers.csv', index=False)
print(f'Combined dataset: {len(combined)} total papers')
"
```

### **Method 2: Manual CSV Creation**

Create a CSV with columns: `id,title,link`

```csv
608,"New Paper Title 1","https://link1.com"
609,"New Paper Title 2","https://link2.com"
...
1107,"New Paper Title 500","https://link500.com"
```

### **Process Combined Dataset**

```bash
python3 nasa_pipeline_simple.py --mode full --verbose
```

---

## 🎛️ **Advanced Usage**

### **Individual Pipeline Stages**

```bash
# Download PDFs only
python3 nasa_pipeline_simple.py --mode download --sample 50

# Extract text only
python3 nasa_pipeline_simple.py --mode extract_text --sample 50

# Generate summaries only
python3 nasa_pipeline_simple.py --mode extractive --sample 50
python3 nasa_pipeline_simple.py --mode abstractive --sample 50

# Topic analysis only
python3 nasa_pipeline_simple.py --mode topic --sample 50
```

### **Model Selection**

```bash
# Use different AI models
python3 nasa_pipeline_simple.py --mode abstractive --abstractive-model bart    # Facebook BART (default)
python3 nasa_pipeline_simple.py --mode abstractive --abstractive-model t5      # Google T5
python3 nasa_pipeline_simple.py --mode abstractive --abstractive-model pegasus # Google Pegasus
```

### **Batch Processing for Large Datasets**

```bash
# Process in smaller batches to avoid memory issues
python3 nasa_pipeline_simple.py --mode download --sample 100
python3 nasa_pipeline_simple.py --mode extract_text --sample 100
python3 nasa_pipeline_simple.py --mode extractive --sample 100
python3 nasa_pipeline_simple.py --mode abstractive --sample 100
python3 nasa_pipeline_simple.py --mode topic --sample 100
```

---

## 📈 **Expected Processing Times**

| Dataset Size | Download  | Text Extract | Extractive | Abstractive | Total Time |
| ------------ | --------- | ------------ | ---------- | ----------- | ---------- |
| 10 papers    | 2-3 min   | 30 sec       | 10 sec     | 2-3 min     | 5-8 min    |
| 100 papers   | 15-20 min | 3-5 min      | 1-2 min    | 20-30 min   | 40-60 min  |
| 607 papers   | 2-3 hours | 15-20 min    | 5-10 min   | 2-3 hours   | 4-6 hours  |
| 1107 papers  | 3-4 hours | 30-40 min    | 10-15 min  | 4-5 hours   | 7-9 hours  |

---

## 🔍 **Understanding the Results**

### **Extractive Summaries**

- Selects the most important sentences from the original text
- Preserves exact wording from the research papers
- Good for maintaining scientific accuracy

### **Abstractive Summaries**

- Uses AI to generate new, concise text
- More readable and coherent
- May paraphrase but maintains key information

### **Topic Analysis**

- Identifies common themes across papers
- Shows word clouds and topic weights
- Helps discover research patterns

---

## 🛠️ **Troubleshooting**

### **PDF Download Issues**

- Some papers may not download due to access restrictions
- The pipeline continues with available papers
- Check logs for specific failure reasons

### **Memory Issues**

- Process in smaller batches using `--sample N`
- Close other applications to free up memory

### **Model Loading Issues**

- Models download automatically on first use
- Ensure internet connection for model downloads
- Models are cached locally after first download

---

## 🎉 **You're Ready to Go!**

Your NASA Bioscience Summarizer is fully functional and ready to process your research data. The program will:

✅ Download PDFs from your CSV links  
✅ Extract and structure text content  
✅ Generate both extractive and AI-powered summaries  
✅ Identify research topics and themes  
✅ Provide an interactive dashboard for exploration

**Start with**: `python3 nasa_pipeline_simple.py --mode full --sample 5 --verbose`  
**Then explore**: `streamlit run dashboard_simple.py`

---

## 📞 **Need Help?**

If you encounter any issues:

1. Check the logs for specific error messages
2. Try processing a smaller sample first
3. Ensure all dependencies are installed
4. Check your internet connection for model downloads

The program is designed to be robust and handle various edge cases gracefully.
