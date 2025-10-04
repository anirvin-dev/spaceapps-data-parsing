#!/bin/bash
# Process 200 Papers Complete Pipeline
# This will take 30-40 minutes

set -e

echo "🚀 Starting Complete Processing of 200 Papers..."
echo "This will take 30-40 minutes. Please wait..."
echo ""

# Stop any running processes
echo "1/6 Stopping any existing processes..."
pkill -f nasa_pipeline_simple 2>/dev/null || true
sleep 2

# Stage 1: Download PDFs (with rate limiting)
echo ""
echo "2/6 Downloading PDFs (10 minutes)..."
python3 nasa_pipeline_simple.py --mode download --sample 200 --verbose

# Stage 2: Extract text
echo ""
echo "3/6 Extracting text from PDFs (2 minutes)..."
python3 nasa_pipeline_simple.py --mode extract_text --sample 200 --verbose

# Stage 3: Extractive summarization
echo ""
echo "4/6 Creating extractive summaries (3 minutes)..."
python3 nasa_pipeline_simple.py --mode extractive --sample 200 --verbose

# Stage 4: Abstractive summarization
echo ""
echo "5/6 Creating abstractive summaries (15 minutes)..."
python3 nasa_pipeline_simple.py --mode abstractive --sample 200 --verbose

# Stage 5: Topic modeling
echo ""
echo "6/6 Running topic modeling (2 minutes)..."
python3 nasa_pipeline_simple.py --mode topic --sample 200 --verbose

# Stage 6: Advanced analysis
echo ""
echo "7/7 Running advanced analysis (claims, gaps, insights)..."
python3 advanced_analysis.py

echo ""
echo "✅ COMPLETE! Processed 200 papers with all features!"
echo ""
echo "📊 Results:"
echo "   - 200 papers with extractive + abstractive summaries"
echo "   - Topic clusters identified"
echo "   - Consensus claims extracted"
echo "   - Knowledge gaps detected"
echo "   - Mission insights generated"
echo ""
echo "🚀 Restart dashboard to see all results:"
echo "   pkill -f streamlit && streamlit run dashboard_complete.py --server.port 8503"

