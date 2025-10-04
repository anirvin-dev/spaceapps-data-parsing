#!/usr/bin/env python3
"""
Export all data as JSON for Framer integration
"""

import json
import pandas as pd
from pathlib import Path

# Directories
ROOT = Path.cwd()
EXPORT_DIR = ROOT / "framer_export"
DATA_CSV = ROOT / "data" / "nasa_papers.csv"
SUM_EX_DIR = ROOT / "summaries" / "extractive"
SUM_AB_DIR = ROOT / "summaries" / "abstractive"
ANALYSIS_DIR = ROOT / "analysis"
ADDITIONAL_DATA_DIR = ROOT / "additional_data"
TOPICS_DIR = ROOT / "topics"

# Create export directory
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def export_papers():
    """Export papers with summaries."""
    print("📄 Exporting papers...")
    
    df = pd.read_csv(DATA_CSV)
    papers_data = []
    
    for _, row in df.iterrows():
        paper_id = str(row['id'])
        
        # Check for summaries
        ex_path = SUM_EX_DIR / f"paper_{paper_id}_summary.txt"
        ab_path = SUM_AB_DIR / f"paper_{paper_id}_summary.txt"
        
        ex_summary = ""
        ab_summary = ""
        has_summary = False
        
        if ex_path.exists():
            with open(ex_path, 'r', encoding='utf-8') as f:
                ex_summary = f.read()
                has_summary = True
        
        if ab_path.exists():
            with open(ab_path, 'r', encoding='utf-8') as f:
                ab_summary = f.read()
        
        paper_data = {
            "id": int(paper_id),
            "title": row['title'],
            "link": row['link'],
            "has_summary": has_summary,
            "extractive_summary": ex_summary,
            "abstractive_summary": ab_summary
        }
        
        papers_data.append(paper_data)
    
    output = {
        "total": len(df),
        "processed": sum(1 for p in papers_data if p['has_summary']),
        "papers": papers_data
    }
    
    with open(EXPORT_DIR / "papers.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(papers_data)} papers ({output['processed']} with summaries)")

def export_claims():
    """Export consensus claims."""
    print("🤝 Exporting consensus claims...")
    
    claims_path = ANALYSIS_DIR / "claims.json"
    if not claims_path.exists():
        print("  ⚠️  No claims found")
        return
    
    with open(claims_path, 'r', encoding='utf-8') as f:
        claims_data = json.load(f)
    
    # Restructure for easier use
    claims_list = []
    for key, claim in claims_data.get('claims', {}).items():
        claim['id'] = key
        claims_list.append(claim)
    
    output = {
        "total_claims": len(claims_list),
        "papers_analyzed": claims_data.get('papers_analyzed', 208),
        "claims": claims_list
    }
    
    with open(EXPORT_DIR / "claims.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(claims_list)} consensus claims")

def export_topics():
    """Export topics with paper details."""
    print("🏷️  Exporting topics...")
    
    topics_path = TOPICS_DIR / "topics.json"
    if not topics_path.exists():
        print("  ⚠️  No topics found")
        return
    
    with open(topics_path, 'r', encoding='utf-8') as f:
        topics_data = json.load(f)
    
    df = pd.read_csv(DATA_CSV)
    
    # Enhance topics with paper titles
    topics_list = []
    for idx, topic in enumerate(topics_data.get('topics', []), start=1):
        rep_docs = topic.get('representative_docs', [])
        papers_with_titles = []
        
        for doc_id in rep_docs[:10]:  # Top 10 papers
            try:
                paper = df[df['id'] == int(doc_id)]
                if not paper.empty:
                    papers_with_titles.append({
                        "id": int(doc_id),
                        "title": paper.iloc[0]['title']
                    })
            except:
                pass
        
        topic_data = {
            "id": idx,  # 1-based numbering
            "name": ", ".join(topic.get('top_words', [])[:5]).title(),
            "keywords": topic.get('top_words', [])[:15],
            "paper_count": len(rep_docs),
            "papers": [int(x) for x in rep_docs[:20]],  # Top 20 paper IDs
            "papers_with_titles": papers_with_titles
        }
        
        topics_list.append(topic_data)
    
    output = {
        "total_topics": len(topics_list),
        "topics": topics_list
    }
    
    with open(EXPORT_DIR / "topics.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(topics_list)} topics")

def export_gaps():
    """Export knowledge gaps."""
    print("🔍 Exporting knowledge gaps...")
    
    gaps_path = ANALYSIS_DIR / "knowledge_gaps.json"
    if not gaps_path.exists():
        print("  ⚠️  No gaps found")
        return
    
    with open(gaps_path, 'r', encoding='utf-8') as f:
        gaps_data = json.load(f)
    
    gaps_list = gaps_data.get('gaps', [])
    
    output = {
        "total_gaps": len(gaps_list),
        "gaps": gaps_list
    }
    
    with open(EXPORT_DIR / "gaps.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(gaps_list)} knowledge gaps")

def export_insights():
    """Export mission insights."""
    print("🚀 Exporting mission insights...")
    
    insights_path = ANALYSIS_DIR / "mission_insights.json"
    if not insights_path.exists():
        print("  ⚠️  No insights found")
        return
    
    with open(insights_path, 'r', encoding='utf-8') as f:
        insights_data = json.load(f)
    
    insights_list = insights_data.get('insights', [])
    
    output = {
        "total_insights": len(insights_list),
        "insights": insights_list
    }
    
    with open(EXPORT_DIR / "insights.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(insights_list)} mission insights")

def export_sources():
    """Export additional NASA sources."""
    print("🌐 Exporting additional sources...")
    
    sources_path = ADDITIONAL_DATA_DIR / "additional_sources.csv"
    if not sources_path.exists():
        print("  ⚠️  No additional sources found")
        return
    
    df = pd.read_csv(sources_path)
    sources_list = df.to_dict('records')
    
    output = {
        "total_sources": len(sources_list),
        "sources": sources_list
    }
    
    with open(EXPORT_DIR / "sources.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Exported {len(sources_list)} additional sources")

def export_stats():
    """Export overall statistics."""
    print("📊 Exporting statistics...")
    
    # Count summaries
    ex_count = len(list(SUM_EX_DIR.glob("*.txt")))
    ab_count = len(list(SUM_AB_DIR.glob("*.txt")))
    
    # Load data
    df = pd.read_csv(DATA_CSV)
    
    claims_path = ANALYSIS_DIR / "claims.json"
    claims_count = 0
    if claims_path.exists():
        with open(claims_path, 'r') as f:
            claims_data = json.load(f)
            claims_count = len(claims_data.get('claims', {}))
    
    sources_path = ADDITIONAL_DATA_DIR / "additional_sources.csv"
    sources_count = 0
    if sources_path.exists():
        sources_df = pd.read_csv(sources_path)
        sources_count = len(sources_df)
    
    stats = {
        "total_papers": len(df),
        "papers_with_summaries": min(ex_count, ab_count),
        "extractive_summaries": ex_count,
        "abstractive_summaries": ab_count,
        "consensus_claims": claims_count,
        "additional_sources": sources_count,
        "total_data_points": len(df) + sources_count,
        "last_updated": "2025-10-04"
    }
    
    with open(EXPORT_DIR / "stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"  ✅ Exported statistics")

def create_readme():
    """Create README for framer_export folder."""
    readme_content = """# Framer Export Data

This folder contains all NASA Bioscience data exported as JSON for Framer integration.

## Files

- `papers.json` - All 607 papers with summaries (200 processed)
- `claims.json` - 15 consensus claims with evidence
- `topics.json` - 10 research topics with papers
- `gaps.json` - 8 knowledge gaps
- `insights.json` - 15 mission insights
- `sources.json` - 1,507 additional NASA sources
- `stats.json` - Overall statistics

## Usage in Framer

```javascript
// Fetch papers
fetch('/api/papers.json')
    .then(res => res.json())
    .then(data => console.log(data.papers))

// Fetch claims
fetch('/api/claims.json')
    .then(res => res.json())
    .then(data => console.log(data.claims))
```

## Data Structure

See FRAMER_INTEGRATION_GUIDE.md for complete documentation.

## Updates

Run `python3 export_for_framer.py` to regenerate all JSON files.

Last updated: 2025-10-04
"""
    
    with open(EXPORT_DIR / "README.md", 'w') as f:
        f.write(readme_content)

def main():
    print("🚀 Exporting data for Framer integration...")
    print("")
    
    export_papers()
    export_claims()
    export_topics()
    export_gaps()
    export_insights()
    export_sources()
    export_stats()
    create_readme()
    
    print("")
    print("✅ SUCCESS! All data exported to framer_export/")
    print("")
    print("📁 Files created:")
    for file in sorted(EXPORT_DIR.glob("*.json")):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name} ({size_kb:.1f} KB)")
    print("")
    print("📖 See FRAMER_INTEGRATION_GUIDE.md for usage instructions")

if __name__ == "__main__":
    main()

