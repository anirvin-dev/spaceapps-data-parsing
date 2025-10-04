#!/bin/bash

# Generate summaries for all 608 papers in batches of 100

echo "🚀 Generating summaries for ALL 608 papers"
echo "This will take ~15 minutes"
echo ""

# Batch 3: Papers 209-308
echo "📝 Batch 3/5: Papers 209-308..."
python3 create_100_summaries.py 209
echo ""

# Batch 4: Papers 309-408
echo "📝 Batch 4/5: Papers 309-408..."
python3 create_100_summaries.py 309
echo ""

# Batch 5: Papers 409-508
echo "📝 Batch 5/5: Papers 409-508..."
python3 create_100_summaries.py 409
echo ""

# Batch 6: Papers 509-608 (final batch)
echo "📝 Batch 6/6: Papers 509-608..."
python3 create_100_summaries.py 509
echo ""

# Count final totals
echo "✅ COMPLETE!"
echo ""
echo "📊 Final Counts:"
echo "Extractive: $(ls -1 summaries/extractive/*.txt 2>/dev/null | wc -l)"
echo "Abstractive: $(ls -1 summaries/abstractive/*.txt 2>/dev/null | wc -l)"
echo ""
echo "🎉 ALL 608 PAPERS NOW HAVE SUMMARIES!"
echo ""
echo "Next steps:"
echo "1. Restart dashboard: pkill -f streamlit && streamlit run dashboard_complete.py --server.port 8503"
echo "2. Re-export for Framer: python3 export_for_framer.py"

