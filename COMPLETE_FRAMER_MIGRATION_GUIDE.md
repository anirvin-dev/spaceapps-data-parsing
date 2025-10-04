# 🎨 COMPLETE FRAMER MIGRATION GUIDE

## Every Bit of Data → Your Custom Design

---

## 📊 STEP 1: UNDERSTAND WHAT YOU HAVE

### Your Complete Dataset (2,114 sources):

```
✅ 607 NASA Papers (100% coverage)
   - Each has: Title, Link, Extractive Summary, Abstractive Summary

✅ 20 Consensus Claims
   - Each has: Claim text, Consensus score (76-96%), Supporting papers count,
     Contradicting papers count, 5 evidence snippets with paper IDs

✅ 10 Topics
   - Each has: Topic name, 15 keywords, Paper count, Representative papers list

✅ 12 Knowledge Gaps
   - Each has: Gap score, Mission relevance, Keywords, 3-4 recommended experiments

✅ 20 Mission Insights
   - Each has: Title, Category, Risk level, Confidence score, Finding text,
     Recommendation text, Supporting papers count

✅ 1,507 Additional NASA Sources
   - Each has: Title, Source type, Category, Link, Description

✅ Overview Stats
   - Total papers, Total sources, Total claims, Total gaps, Total insights
```

---

## 📁 STEP 2: COPY YOUR DATA TO FRAMER

### A. Create Folder Structure in Framer

In your Framer project root:

```
your-framer-project/
├── public/
│   └── api/
│       ├── papers.json          (copy this)
│       ├── claims.json          (copy this)
│       ├── topics.json          (copy this)
│       ├── gaps.json            (copy this)
│       ├── insights.json        (copy this)
│       ├── sources.json         (copy this)
│       └── stats.json           (copy this)
```

### B. Copy Command (from your Mac terminal):

```bash
# Navigate to your Framer project
cd /path/to/your/framer/project

# Create the api folder
mkdir -p public/api

# Copy all JSON files
cp /Applications/SpaceAppsHackatho/spaceapps-data-parsing/framer_export/*.json public/api/
```

---

## 🎨 STEP 3: DATA STRUCTURE REFERENCE

### 1️⃣ PAPERS DATA (`papers.json`)

**Access:** `fetch('/api/papers.json')`

**Structure:**

```typescript
{
  "papers": [
    {
      "id": 1,
      "title": "Paper title...",
      "link": "https://pmc.ncbi.nlm.nih.gov/...",
      "extractive_summary": "Key findings extracted...",
      "abstractive_summary": "AI-generated concise summary...",
      "has_summary": true
    },
    // ... 606 more papers
  ],
  "total_papers": 607,
  "papers_with_summaries": 607
}
```

**What to Display:**

- 📄 List view: Title + short excerpt
- 🔍 Detail view: Full title, both summaries, link to paper
- 🏷️ Filters: By topic, search by title/summary
- 📊 Stats: Total count (607)

---

### 2️⃣ CONSENSUS CLAIMS (`claims.json`)

**Access:** `fetch('/api/claims.json')`

**Structure:**

```typescript
{
  "claims": {
    "microgravity_reduces_bone_density": {
      "normalized_claim": "microgravity_reduces_bone_density",
      "claim": "Microgravity reduces bone density",
      "consensus_score": 93,
      "confidence_badge": "strong_consensus",
      "supporting_papers": 187,
      "contradicting_papers": 8,
      "supporting_snippets": [
        {
          "paper_id": "15",
          "section": "results",
          "sentence": "Bone mineral density decreased by 1.5% per month..."
        },
        // ... 4 more snippets
      ]
    },
    // ... 19 more claims
  },
  "total_claims": 20
}
```

**What to Display:**

- 🎯 Cards: Claim + consensus % + badge color
- 📊 Progress bar: Consensus score (76-96%)
- 📝 Evidence: Show supporting vs contradicting counts
- 💬 Expandable: Show 5 evidence snippets on click
- 🔢 Paper count: "Based on 187 papers"
- 🏷️ Badge: "Strong Consensus" (green) or "Moderate Consensus" (yellow)

**Color Coding:**

```css
strong_consensus (>85%): #10b981 (green)
moderate_consensus (<85%): #f59e0b (yellow)
```

---

### 3️⃣ TOPICS (`topics.json`)

**Access:** `fetch('/api/topics.json')`

**Structure:**

```typescript
{
  "topics": [
    {
      "topic_id": 1,
      "name": "Musculoskeletal Adaptation & Countermeasures",
      "top_words": ["bone", "muscle", "atrophy", "exercise", ...],
      "representative_docs": [1, 2, 3, ..., 100],
      "paper_count": 100,
      "papers_with_titles": [
        {"id": 1, "title": "Paper title..."},
        // ... 19 more for preview
      ]
    },
    // ... 9 more topics
  ],
  "total_topics": 10
}
```

**What to Display:**

- 📊 Grid/Cards: Topic name + paper count
- 🏷️ Keyword cloud: Top 10-15 keywords
- 📄 Papers: Show representative papers (up to 20)
- 🔢 Count: "100 papers in this topic"
- 🎨 Visual: Use different colors for each topic

**Suggested Topic Colors:**

```css
Topic 1: #3b82f6 (blue)
Topic 2: #8b5cf6 (purple)
Topic 3: #ec4899 (pink)
Topic 4: #f59e0b (orange)
Topic 5: #10b981 (green)
Topic 6: #06b6d4 (cyan)
Topic 7: #6366f1 (indigo)
Topic 8: #f43f5e (red)
Topic 9: #84cc16 (lime)
Topic 10: #a855f7 (violet)
```

---

### 4️⃣ KNOWLEDGE GAPS (`gaps.json`)

**Access:** `fetch('/api/gaps.json')`

**Structure:**

```typescript
{
  "gaps": [
    {
      "gap_score": 0.89,
      "keywords": ["long-term", "mars", "radiation", "deep-space"],
      "mission_relevance": 0.95,
      "paper_density": 23,
      "recommended_experiments": [
        "Long-duration radiation exposure studies beyond LEO",
        "Investigate combined effects of radiation and microgravity",
        "Study radiation countermeasure efficacy for Mars missions",
        "Assess long-term cognitive effects of deep-space radiation"
      ]
    },
    // ... 11 more gaps
  ],
  "total_gaps": 12
}
```

**What to Display:**

- 🎯 Cards: Keywords + gap score %
- 📊 Scores: Gap score (72-89%) + Mission relevance (85-95%)
- 🔬 Experiments: List 3-4 recommended studies
- 📝 Summary: "Only 23 papers cover this critical area"
- 🚨 Priority: High (>85%), Medium (75-85%), Low (<75%)

**Priority Color Coding:**

```css
High (>85%): #ef4444 (red)
Medium (75-85%): #f59e0b (orange)
Low (<75%): #3b82f6 (blue)
```

---

### 5️⃣ MISSION INSIGHTS (`insights.json`)

**Access:** `fetch('/api/insights.json')`

**Structure:**

```typescript
{
  "insights": [
    {
      "title": "Bone Loss Requires Multi-Modal Countermeasures",
      "category": "Musculoskeletal",
      "risk_level": "high",
      "confidence": 93.5,
      "finding": "Despite exercise protocols, significant bone loss persists...",
      "recommendation": "Implement combined countermeasures: high-intensity resistance...",
      "supporting_papers": 187
    },
    // ... 19 more insights
  ],
  "total_insights": 20
}
```

**What to Display:**

- 🎯 Cards: Title + risk level badge + confidence %
- 📊 Confidence: Show as % or progress bar
- 📝 Finding: Key research finding (2-3 sentences)
- 💡 Recommendation: Actionable advice
- 🔢 Support: "Based on 187 papers"
- 🏷️ Category: Musculoskeletal, Radiation, Immunology, etc.

**Risk Level Color Coding:**

```css
High: #ef4444 (red) 🔴
Medium: #f59e0b (orange) 🟡
Low: #10b981 (green) 🟢
```

---

### 6️⃣ ADDITIONAL SOURCES (`sources.json`)

**Access:** `fetch('/api/sources.json')`

**Structure:**

```typescript
{
  "sources": [
    {
      "source_id": "OSDR_001",
      "title": "Source title...",
      "source": "NASA OSDR",
      "type": "Space Biology Research",
      "category": "Microgravity Studies",
      "url": "https://...",
      "description": "Description of experiment..."
    },
    // ... 1,506 more sources
  ],
  "total_sources": 1507
}
```

**What to Display:**

- 📄 List: Title + source type
- 🏷️ Filters: By source (OSDR, Task Book, Missions, PSI)
- 🔍 Search: By title, category
- 🔗 Link: Direct link to original source
- 📊 Count: "1,507 additional NASA sources"

**Source Type Colors:**

```css
NASA OSDR: #3b82f6 (blue)
Task Book: #10b981 (green)
NASA Missions: #f59e0b (orange)
PSI Experiments: #8b5cf6 (purple)
```

---

### 7️⃣ OVERVIEW STATS (`stats.json`)

**Access:** `fetch('/api/stats.json')`

**Structure:**

```typescript
{
  "total_papers": 607,
  "papers_with_summaries": 607,
  "total_sources": 2114,
  "total_claims": 20,
  "total_topics": 10,
  "total_gaps": 12,
  "total_insights": 20
}
```

**What to Display:**

- 📊 Dashboard cards: Big numbers with labels
- 🎨 Visual: Icons + colors for each stat
- 📈 Charts: Optional pie/bar charts

---

## 💻 STEP 4: FRAMER IMPLEMENTATION

### A. Create Data Hook (Reusable)

Create: `hooks/useData.ts`

```typescript
import { useState, useEffect } from "react";

export function usePapers() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

// Repeat for other data types
export function useClaims() {
  /* ... */
}
export function useTopics() {
  /* ... */
}
export function useGaps() {
  /* ... */
}
export function useInsights() {
  /* ... */
}
export function useSources() {
  /* ... */
}
export function useStats() {
  /* ... */
}
```

---

### B. Example Component: Papers Page

```typescript
import { usePapers } from "./hooks/useData";

export default function PapersPage() {
  const { data, loading } = usePapers();

  if (loading) return <div>Loading...</div>;

  const papers = data.papers.filter((p) => p.has_summary);

  return (
    <div className="papers-grid">
      <h1>All {papers.length} NASA Papers</h1>

      {/* Search Bar */}
      <input
        type="search"
        placeholder="Search papers..."
        className="search-bar"
      />

      {/* Papers Grid */}
      {papers.map((paper) => (
        <div key={paper.id} className="paper-card">
          <h3>{paper.title}</h3>

          <div className="summaries">
            <div>
              <strong>Key Findings:</strong>
              <p>{paper.extractive_summary.slice(0, 200)}...</p>
            </div>

            <div>
              <strong>Summary:</strong>
              <p>{paper.abstractive_summary}</p>
            </div>
          </div>

          <a href={paper.link} target="_blank">
            Read Full Paper →
          </a>
        </div>
      ))}
    </div>
  );
}
```

---

### C. Example Component: Consensus Claims

```typescript
import { useClaims } from "./hooks/useData";

export default function ClaimsPage() {
  const { data, loading } = useClaims();

  if (loading) return <div>Loading...</div>;

  const claimsArray = Object.values(data.claims);
  const sortedClaims = claimsArray.sort(
    (a, b) => b.consensus_score - a.consensus_score
  );

  return (
    <div className="claims-container">
      <h1>Scientific Consensus ({data.total_claims} Claims)</h1>

      {sortedClaims.map((claim) => (
        <div key={claim.normalized_claim} className="claim-card">
          {/* Header */}
          <div className="claim-header">
            <h3>{claim.claim}</h3>
            <span
              className={`badge ${claim.confidence_badge}`}
              style={{
                backgroundColor:
                  claim.consensus_score > 85 ? "#10b981" : "#f59e0b",
              }}
            >
              {claim.consensus_score}% Consensus
            </span>
          </div>

          {/* Evidence Count */}
          <div className="evidence-stats">
            <span>✅ {claim.supporting_papers} supporting</span>
            <span>❌ {claim.contradicting_papers} contradicting</span>
          </div>

          {/* Progress Bar */}
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${claim.consensus_score}%` }}
            />
          </div>

          {/* Evidence Snippets (Expandable) */}
          <details>
            <summary>Show Evidence</summary>
            {claim.supporting_snippets.map((snippet, idx) => (
              <div key={idx} className="snippet">
                <strong>Paper {snippet.paper_id}:</strong>
                <p>"{snippet.sentence}"</p>
              </div>
            ))}
          </details>
        </div>
      ))}
    </div>
  );
}
```

---

### D. Example Component: Topics

```typescript
import { useTopics } from "./hooks/useData";

export default function TopicsPage() {
  const { data, loading } = useTopics();

  if (loading) return <div>Loading...</div>;

  const topicColors = [
    "#3b82f6",
    "#8b5cf6",
    "#ec4899",
    "#f59e0b",
    "#10b981",
    "#06b6d4",
    "#6366f1",
    "#f43f5e",
    "#84cc16",
    "#a855f7",
  ];

  return (
    <div className="topics-grid">
      <h1>Research Topics ({data.total_topics})</h1>

      {data.topics.map((topic, idx) => (
        <div
          key={topic.topic_id}
          className="topic-card"
          style={{ borderColor: topicColors[idx] }}
        >
          <div className="topic-header">
            <h3>{topic.name}</h3>
            <span className="count">{topic.paper_count} papers</span>
          </div>

          {/* Keywords */}
          <div className="keywords">
            {topic.top_words.slice(0, 10).map((word) => (
              <span key={word} className="keyword-tag">
                {word}
              </span>
            ))}
          </div>

          {/* Representative Papers */}
          <details>
            <summary>View Papers</summary>
            {topic.papers_with_titles.map((paper) => (
              <div key={paper.id} className="paper-link">
                Paper {paper.id}: {paper.title}
              </div>
            ))}
          </details>
        </div>
      ))}
    </div>
  );
}
```

---

## 🎯 STEP 5: PAGE STRUCTURE RECOMMENDATION

### Suggested Pages for Your Framer Site:

```
1. 🏠 HOME / OVERVIEW
   - Hero section with project description
   - Big stats cards (607 papers, 2,114 sources, etc.)
   - Quick links to other sections

2. 📚 PAPERS
   - Searchable/filterable list of all 607 papers
   - Card view with extractive + abstractive summaries
   - Link to original papers

3. 🎯 CONSENSUS CLAIMS
   - 20 claims with consensus scores
   - Evidence snippets
   - Visual progress bars

4. 🏷️ TOPICS
   - 10 topic cards with keywords
   - Paper counts per topic
   - Representative papers list

5. 🔬 RESEARCH GAPS
   - 12 knowledge gaps
   - Mission relevance scores
   - Recommended experiments

6. 🚀 MISSION INSIGHTS
   - 20 actionable recommendations
   - Risk levels and confidence scores
   - Categories and findings

7. 🌐 DATA SOURCES
   - 1,507 additional NASA sources
   - Filter by source type
   - Direct links

8. 🔍 SEARCH (Optional)
   - Global search across all data
```

---

## 🎨 STEP 6: STYLING TIPS

### Color Palette (Match to your Framer theme):

```css
/* Backgrounds */
--bg-primary: #ffffff;
--bg-secondary: #f9fafb;
--bg-tertiary: #f3f4f6;

/* Text */
--text-primary: #111827;
--text-secondary: #6b7280;
--text-accent: #3b82f6;

/* Status Colors */
--success: #10b981;
--warning: #f59e0b;
--danger: #ef4444;
--info: #3b82f6;

/* Consensus Badges */
--strong-consensus: #10b981;
--moderate-consensus: #f59e0b;

/* Risk Levels */
--risk-high: #ef4444;
--risk-medium: #f59e0b;
--risk-low: #10b981;
```

---

## ✅ STEP 7: IMPLEMENTATION CHECKLIST

### Phase 1: Setup (15 min)

- [ ] Copy 7 JSON files to Framer `public/api/`
- [ ] Create `hooks/useData.ts` with all data hooks
- [ ] Test one fetch to confirm files load

### Phase 2: Core Pages (2-3 hours)

- [ ] Home/Overview page with stats
- [ ] Papers page with search
- [ ] Consensus Claims page
- [ ] Topics page
- [ ] Knowledge Gaps page
- [ ] Mission Insights page
- [ ] Additional Sources page

### Phase 3: Polish (1 hour)

- [ ] Add loading states
- [ ] Add error handling
- [ ] Responsive design adjustments
- [ ] Color theme consistency
- [ ] Typography polish

### Phase 4: Testing (30 min)

- [ ] Test all data loads correctly
- [ ] Test search/filter functionality
- [ ] Test on mobile
- [ ] Test all links work

---

## 📊 QUICK REFERENCE: DATA MAPPING

| Dashboard Page     | JSON File       | Key Fields                     | Display As                   |
| ------------------ | --------------- | ------------------------------ | ---------------------------- |
| Overview           | `stats.json`    | All counts                     | Big number cards             |
| Paper Explorer     | `papers.json`   | title, summaries, link         | Cards with summaries         |
| Topic Analysis     | `topics.json`   | name, keywords, papers         | Topic cards + keyword clouds |
| Search             | All files       | All text fields                | Search results               |
| Consensus Claims   | `claims.json`   | claim, score, evidence         | Cards with progress bars     |
| Knowledge Gaps     | `gaps.json`     | keywords, experiments          | Cards with recommendations   |
| Mission Insights   | `insights.json` | title, finding, recommendation | Cards with risk badges       |
| Additional Sources | `sources.json`  | title, source, link            | Filterable list              |

---

## 🚀 EXAMPLE: MINIMAL WORKING PAGE

Here's a complete minimal example to get you started:

```typescript
// pages/overview.tsx
import { useState, useEffect } from "react";

export default function Overview() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch("/api/stats.json")
      .then((res) => res.json())
      .then((data) => setStats(data));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div style={{ padding: "40px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>NASA Bioscience Knowledge Engine</h1>
      <p>Complete analysis of NASA's bioscience research catalog</p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "20px",
          marginTop: "40px",
        }}
      >
        <StatCard
          title="Papers Analyzed"
          value={stats.total_papers}
          color="#3b82f6"
        />
        <StatCard
          title="Total Sources"
          value={stats.total_sources}
          color="#10b981"
        />
        <StatCard
          title="Consensus Claims"
          value={stats.total_claims}
          color="#f59e0b"
        />
        <StatCard
          title="Mission Insights"
          value={stats.total_insights}
          color="#ef4444"
        />
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div
      style={{
        padding: "30px",
        borderRadius: "12px",
        backgroundColor: color,
        color: "white",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "48px", fontWeight: "bold" }}>{value}</div>
      <div style={{ fontSize: "16px", marginTop: "10px" }}>{title}</div>
    </div>
  );
}
```

---

## 💡 PRO TIPS

1. **Start Small**: Build one page first (Overview), test it works, then expand
2. **Cache Data**: Use localStorage to cache fetched JSON for better performance
3. **Lazy Load**: Use React.lazy() for code splitting on larger pages
4. **Search**: Use simple `.filter()` for client-side search (fast with 607 papers)
5. **Pagination**: If needed, show 20-50 papers at a time with "Load More"
6. **Mobile**: Make sure cards stack vertically on mobile (use CSS Grid)
7. **Loading States**: Always show loading indicators during data fetch
8. **Error Handling**: Add try/catch to handle fetch failures gracefully

---

## 🎯 EXPECTED RESULT

After following this guide, you'll have:

✅ All 607 papers searchable and browsable
✅ 20 consensus claims with evidence
✅ 10 topics with keywords and papers
✅ 12 knowledge gaps with recommendations
✅ 20 mission insights with risk levels
✅ 1,507 additional sources integrated
✅ Clean, theme-matched design in Framer
✅ Production-ready for hackathon presentation

---

## 📞 NEXT STEPS

1. Copy the 7 JSON files to Framer
2. Create your first page (Overview recommended)
3. Test that data loads
4. Build remaining pages one by one
5. Polish styling to match your theme
6. Deploy and present!

---

**🎉 You have EVERYTHING you need. The data is complete, structured, and ready to display. Just fetch, map, and style! GO WIN! 🚀**
