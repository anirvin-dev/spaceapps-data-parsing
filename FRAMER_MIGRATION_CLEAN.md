# 🎨 Framer Migration - What You Need

## ✅ **KEEP - Essential for Framer**

### **📁 Data Files (Required)**

```
framer_export/              ← COPY THIS ENTIRE FOLDER TO FRAMER
├── papers.json             ← All 200 papers with summaries
├── claims.json             ← 15 consensus claims
├── topics.json             ← 10 topics with sources
├── gaps.json               ← Knowledge gaps
├── insights.json           ← Mission insights
├── sources.json            ← 1,507 NASA sources
└── stats.json              ← Overall statistics
```

**Action:** Copy `framer_export/` folder to your Framer project assets

---

### **📋 Documentation (Reference)**

```
FRAMER_INTEGRATION_GUIDE.md    ← Complete integration instructions
COMPLETE_STATUS_200_PAPERS.md  ← What data you have
JUDGE_PRESENTATION_CHEATSHEET.md ← Demo script
```

**Action:** Keep these for reference when building Framer components

---

## ❌ **DELETE - Not Needed for Framer**

### **🗑️ Pipeline Scripts (Backend Only)**

```
nasa_pipeline_simple.py         ← PDF processing pipeline
nasa_pipeline_all_in_one.py     ← Original pipeline
advanced_analysis.py            ← Analysis generation
create_100_summaries.py         ← Summary generator
create_enhanced_claims.py       ← Claims generator
create_demo_analysis.py         ← Demo data creator
create_demo_topics.py           ← Topic generator
create_clean_summaries.py       ← Summary cleaner
nasa_data_scraper.py           ← Web scraper
integrate_nasa_sources.py      ← Source integrator
expand_nasa_data_massively.py  ← Data expander
add_ids_to_csv.py              ← CSV utility
test_pipeline.py               ← Test script
process_200_papers.sh          ← Bash script
```

**Why Delete:** These generate the data. You already have the final JSON files.

---

### **🗑️ Dashboard Files (Streamlit Only)**

```
dashboard_complete.py           ← Streamlit dashboard
dashboard_simple.py            ← Simple dashboard
dashboard_enhanced.py          ← Enhanced dashboard
dashboard.py                   ← Original dashboard
```

**Why Delete:** You're building UI in Framer, not using Streamlit.

---

### **🗑️ Raw Data Directories**

```
papers/                    ← PDFs (not needed in web app)
paper_text/               ← Extracted text (not needed)
summaries/extractive/     ← Already in papers.json
summaries/abstractive/    ← Already in papers.json
topics/topics.json        ← Already in framer_export/topics.json
analysis/                 ← Already in framer_export/
```

**Why Delete:** All this data is compiled in `framer_export/` JSON files.

---

### **🗑️ Source CSVs**

```
data/nasa_papers.csv              ← Already in papers.json
data/SB_publication_PMC.csv       ← Original raw data
additional_data/*.csv             ← Already in sources.json
```

**Why Delete:** JSON files are more web-friendly than CSVs.

---

### **🗑️ Python Environment**

```
venv/                     ← Virtual environment
requirements.txt          ← Python dependencies
```

**Why Delete:** Framer doesn't need Python.

---

### **🗑️ Documentation (Optional)**

```
README.md                          ← Project setup
QUICKSTART.md                      ← Setup instructions
COMPLETE_USER_GUIDE.md             ← User guide
PMC_RATE_LIMITING_SOLUTION.md      ← Technical notes
FIXES_APPLIED.md                   ← Development notes
DEMO_READY_NOW.md                  ← Demo status
DEMO_STATUS_100_PAPERS.md          ← Old status
PROCESSING_200_PAPERS.md           ← Processing notes
PROJECT_STATUS.md                  ← Status update
FINAL_STATUS.md                    ← Final status
HACKATHON_FEATURES.md              ← Feature list
```

**Why Delete:** These are development docs, not needed for live site.

---

## 📦 **Minimal Framer Package**

### **What to Copy to Framer:**

```
your-framer-project/
└── public/                        ← Or wherever Framer stores assets
    └── api/                       ← Create this folder
        ├── papers.json            ← Copy from framer_export/
        ├── claims.json            ← Copy from framer_export/
        ├── topics.json            ← Copy from framer_export/
        ├── gaps.json              ← Copy from framer_export/
        ├── insights.json          ← Copy from framer_export/
        ├── sources.json           ← Copy from framer_export/
        └── stats.json             ← Copy from framer_export/
```

**Total Size:** ~940 KB (7 JSON files)

---

## 🎨 **Framer Component Architecture**

### **Recommended Page Structure:**

```
your-framer-site/
├── Home                           ← Hero + Stats
├── Papers                         ← Browse 200 papers
├── Topics                         ← 10 research topics
├── Insights                       ← Claims, Gaps, Mission Insights
└── Sources                        ← 1,507 NASA sources
```

---

### **Component Hierarchy:**

```
App
├── Navbar
├── HomePage
│   ├── HeroSection (stats from stats.json)
│   ├── FeaturedPapers (from papers.json)
│   └── TopicCarousel (from topics.json)
├── PapersPage
│   ├── SearchBar
│   ├── FilterBar (by topic)
│   └── PaperGrid
│       └── PaperCard (extractive + abstractive)
├── TopicsPage
│   ├── TopicList
│   └── TopicDetail
│       └── PapersList
├── InsightsPage
│   ├── ConsensusClaims (from claims.json)
│   ├── KnowledgeGaps (from gaps.json)
│   └── MissionInsights (from insights.json)
└── SourcesPage
    ├── FilterBar (by source type)
    └── SourceGrid
```

---

## 🔧 **Data Fetching Pattern**

### **Use React Hooks in Framer:**

```typescript
import { useState, useEffect } from "react";

export function usePapers() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => {
        setPapers(data.papers);
        setLoading(false);
      });
  }, []);

  return { papers, loading };
}

// Use in component:
export function PapersPage() {
  const { papers, loading } = usePapers();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {papers
        .filter((p) => p.has_summary)
        .map((paper) => (
          <PaperCard key={paper.id} paper={paper} />
        ))}
    </div>
  );
}
```

---

## 📊 **Data Structure Reference**

### **Papers (papers.json):**

```typescript
interface Paper {
  id: number;
  title: string;
  link: string;
  has_summary: boolean;
  extractive_summary: string;
  abstractive_summary: string;
}

// Access:
papers.filter((p) => p.has_summary); // Get 200 with summaries
```

### **Topics (topics.json):**

```typescript
interface Topic {
  id: number; // 1-10
  name: string;
  keywords: string[]; // Top 15 keywords
  paper_count: number;
  papers: number[]; // Paper IDs
  papers_with_titles: {
    id: number;
    title: string;
  }[];
}

// Access:
topics.find((t) => t.id === 1); // Get specific topic
```

### **Claims (claims.json):**

```typescript
interface Claim {
  id: string;
  claim: string;
  consensus_score: number; // 0-100
  confidence_badge: "strong_consensus" | "moderate_consensus";
  supporting_papers: number;
  contradicting_papers: number;
  supporting_snippets: {
    paper_id: string;
    section: string;
    sentence: string;
  }[];
}

// Access:
claims.filter((c) => c.consensus_score > 80); // High confidence
```

### **Sources (sources.json):**

```typescript
interface Source {
  id: string;
  title: string;
  source: "NASA OSDR" | "NASA Task Book" | etc;
  type: "Experiment" | "Project" | "Mission";
  category: string;
  url: string;
}

// Access:
sources.filter((s) => s.source === "NASA OSDR");
```

---

## 🎯 **Migration Checklist**

### **Step 1: Setup Framer Project**

- [ ] Create new Framer project or open existing
- [ ] Create `/public/api/` folder (or appropriate location)
- [ ] Copy all 7 JSON files from `framer_export/`

### **Step 2: Create Data Hooks**

- [ ] Create `usePapers()` hook
- [ ] Create `useTopics()` hook
- [ ] Create `useClaims()` hook
- [ ] Create `useGaps()` hook
- [ ] Create `useInsights()` hook
- [ ] Create `useSources()` hook

### **Step 3: Build Pages**

- [ ] Home page with stats
- [ ] Papers page with search/filter
- [ ] Topics page with explorer
- [ ] Insights page (claims + gaps + insights)
- [ ] Sources page with filters

### **Step 4: Create Components**

- [ ] PaperCard (shows extractive + abstractive)
- [ ] TopicCard (shows keywords + paper count)
- [ ] ClaimCard (shows evidence + confidence)
- [ ] GapCard (shows recommendations)
- [ ] InsightCard (shows risk level)
- [ ] SourceCard (shows NASA link)

### **Step 5: Polish**

- [ ] Add loading states
- [ ] Add error handling
- [ ] Style to match your design
- [ ] Test all filters
- [ ] Test all links

---

## 🚀 **Quick Start Command**

### **Export Latest Data (if needed):**

```bash
cd /Applications/SpaceAppsHackatho/spaceapps-data-parsing
python3 export_for_framer.py
```

Then copy `framer_export/` to your Framer project.

---

## 💡 **Pro Tips**

### **1. Use Static JSON (Recommended)**

- Simpler, faster, no backend needed
- Perfect for hackathon demo
- All data pre-computed

### **2. Component Reusability**

```typescript
// Generic card component
export function DataCard({ title, content, link, badge }) {
  return (
    <div className="card">
      {badge && <span className="badge">{badge}</span>}
      <h3>{title}</h3>
      <p>{content}</p>
      {link && <a href={link}>View More →</a>}
    </div>
  );
}

// Use for papers, claims, gaps, insights
```

### **3. Search Implementation**

```typescript
const [search, setSearch] = useState("");
const filtered = papers.filter(
  (p) =>
    p.title.toLowerCase().includes(search.toLowerCase()) ||
    p.abstractive_summary.toLowerCase().includes(search.toLowerCase())
);
```

### **4. Pagination**

```typescript
const [page, setPage] = useState(1);
const perPage = 20;
const paginated = filtered.slice((page - 1) * perPage, page * perPage);
```

---

## 📝 **Files to Keep for Reference:**

1. `FRAMER_INTEGRATION_GUIDE.md` - Complete examples
2. `COMPLETE_STATUS_200_PAPERS.md` - What you have
3. `JUDGE_PRESENTATION_CHEATSHEET.md` - Demo script

---

## ✨ **Bottom Line**

**Keep:**

- `framer_export/` folder (7 JSON files)
- 3 documentation files for reference

**Delete:**

- Everything else (20+ Python scripts, Streamlit dashboard, raw data)

**Result:**

- Clean ~1MB package ready for Framer
- All data accessible via simple fetch
- No backend needed
- Ready to style with your UI

**READY TO BUILD YOUR FRAMER UI! 🎨🚀**
