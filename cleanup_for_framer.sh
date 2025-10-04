#!/bin/bash

# Cleanup script - removes unnecessary files for Framer migration
# This keeps only what you need: framer_export/ and key docs

echo "🧹 Cleaning up codebase for Framer migration..."
echo ""
echo "⚠️  WARNING: This will delete files you don't need for Framer."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Create backup directory
echo "📦 Creating backup in ../spaceapps-backup/..."
mkdir -p ../spaceapps-backup
cp -r . ../spaceapps-backup/

echo ""
echo "🗑️  Removing unnecessary files..."

# Remove Python scripts
rm -f nasa_pipeline_simple.py
rm -f nasa_pipeline_all_in_one.py
rm -f advanced_analysis.py
rm -f create_100_summaries.py
rm -f create_enhanced_claims.py
rm -f create_demo_analysis.py
rm -f create_demo_topics.py
rm -f create_clean_summaries.py
rm -f nasa_data_scraper.py
rm -f integrate_nasa_sources.py
rm -f expand_nasa_data_massively.py
rm -f add_ids_to_csv.py
rm -f test_pipeline.py
rm -f export_for_framer.py
echo "✅ Removed Python scripts"

# Remove dashboard files
rm -f dashboard_complete.py
rm -f dashboard_simple.py
rm -f dashboard_enhanced.py
rm -f dashboard.py
echo "✅ Removed dashboard files"

# Remove shell scripts
rm -f process_200_papers.sh
echo "✅ Removed shell scripts"

# Remove Python environment
rm -rf venv/
rm -f requirements.txt
echo "✅ Removed Python environment"

# Remove raw data directories
rm -rf papers/
rm -rf paper_text/
rm -rf summaries/
rm -rf topics/
rm -rf analysis/
echo "✅ Removed raw data directories"

# Remove source data
rm -rf data/
rm -rf additional_data/
echo "✅ Removed source CSV files"

# Remove extra documentation
rm -f README.md
rm -f QUICKSTART.md
rm -f COMPLETE_USER_GUIDE.md
rm -f PMC_RATE_LIMITING_SOLUTION.md
rm -f FIXES_APPLIED.md
rm -f DEMO_READY_NOW.md
rm -f DEMO_STATUS_100_PAPERS.md
rm -f PROCESSING_200_PAPERS.md
rm -f PROJECT_STATUS.md
rm -f FINAL_STATUS.md
rm -f HACKATHON_FEATURES.md
echo "✅ Removed extra documentation"

# Remove git files (optional)
rm -rf .git/
rm -f .gitignore
echo "✅ Removed git files"

# Remove system files
rm -f .DS_Store
find . -name ".DS_Store" -delete
echo "✅ Removed system files"

echo ""
echo "✅ CLEANUP COMPLETE!"
echo ""
echo "📁 What's left:"
ls -lah
echo ""
echo "📋 You should now have:"
echo "   - framer_export/ (7 JSON files)"
echo "   - FRAMER_INTEGRATION_GUIDE.md"
echo "   - COMPLETE_STATUS_200_PAPERS.md"
echo "   - JUDGE_PRESENTATION_CHEATSHEET.md"
echo "   - FRAMER_MIGRATION_CLEAN.md"
echo ""
echo "📦 Full backup saved in ../spaceapps-backup/"
echo ""
echo "🎨 Ready to copy framer_export/ to your Framer project!"

