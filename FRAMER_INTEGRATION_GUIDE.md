# 🎨 Framer Integration Guide

## 📊 **Current Data Status**

- ✅ **200 Papers** with dual summaries
- ✅ **1,507 Additional NASA Sources**
- ✅ **15 Consensus Claims** (based on 208 papers)
- ✅ **8 Knowledge Gaps**
- ✅ **15 Mission Insights**
- ✅ **10 Topic Clusters** (numbered 1-10 with source papers)

---

## 🔌 **Integration Options**

### **Option 1: Export Data as JSON for Framer**

The easiest way to integrate with Framer is to export all data as JSON files that Framer can fetch.

#### **Step 1: Create Export Script**

I'll create a script that exports all data to a `framer_export/` folder as JSON.

#### **Step 2: Use Framer's Fetch API**

In Framer, use the built-in fetch to load JSON:

```javascript
// In Framer Code Component
import { useState, useEffect } from "react";

export function NASADashboard() {
  const [papers, setPapers] = useState([]);
  const [claims, setClaims] = useState([]);
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    // Fetch papers
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => setPapers(data.papers));

    // Fetch claims
    fetch("/api/claims.json")
      .then((res) => res.json())
      .then((data) => setClaims(data.claims));

    // Fetch topics
    fetch("/api/topics.json")
      .then((res) => res.json())
      .then((data) => setTopics(data.topics));
  }, []);

  return <div>{/* Your Framer UI components here */}</div>;
}
```

---

### **Option 2: Create a FastAPI Backend**

For more dynamic integration, create a REST API that Framer can query.

#### **API Endpoints**

```
GET  /api/papers                    # List all papers
GET  /api/papers/{id}               # Get single paper with summaries
GET  /api/papers/{id}/summary       # Get summaries for a paper
GET  /api/topics                    # List all topics
GET  /api/topics/{id}               # Get topic details with papers
GET  /api/claims                    # List all consensus claims
GET  /api/claims/{id}               # Get claim with evidence
GET  /api/gaps                      # List knowledge gaps
GET  /api/insights                  # List mission insights
GET  /api/sources                   # List additional NASA sources
GET  /api/search?q={query}          # Search papers by keyword
```

---

## 📁 **Exported Data Structure**

### **1. Papers (`papers.json`)**

```json
{
  "total": 607,
  "processed": 200,
  "papers": [
    {
      "id": 1,
      "title": "Paper title...",
      "link": "https://pmc.ncbi.nlm.nih.gov/...",
      "has_summary": true,
      "extractive_summary": "Key findings...",
      "abstractive_summary": "Readable overview...",
      "topics": [1, 5]
    }
  ]
}
```

### **2. Consensus Claims (`claims.json`)**

```json
{
  "total_claims": 15,
  "papers_analyzed": 208,
  "claims": [
    {
      "id": "microgravity_reduces_bone_density",
      "claim": "Microgravity reduces bone density",
      "consensus_score": 92,
      "confidence": "strong_consensus",
      "supporting_papers": 45,
      "contradicting_papers": 2,
      "evidence": [
        {
          "paper_id": 15,
          "section": "results",
          "quote": "Bone mineral density decreased..."
        }
      ]
    }
  ]
}
```

### **3. Topics (`topics.json`)**

```json
{
  "total_topics": 10,
  "topics": [
    {
      "id": 1,
      "name": "Bone & Muscle Degradation",
      "keywords": ["bone", "muscle", "atrophy", "calcium"],
      "paper_count": 85,
      "papers": [15, 22, 28, 45, 67],
      "papers_with_titles": [{ "id": 15, "title": "Bone loss in..." }]
    }
  ]
}
```

### **4. Knowledge Gaps (`gaps.json`)**

```json
{
  "total_gaps": 8,
  "gaps": [
    {
      "id": 1,
      "gap_score": 0.85,
      "keywords": ["long-term", "mars", "radiation"],
      "mission_relevance": 0.92,
      "paper_density": 12,
      "recommended_experiments": [
        "Study long-term radiation effects...",
        "Investigate countermeasures..."
      ]
    }
  ]
}
```

### **5. Mission Insights (`insights.json`)**

```json
{
  "total_insights": 15,
  "insights": [
    {
      "id": 1,
      "title": "Bone Loss Requires Countermeasures",
      "category": "Musculoskeletal",
      "risk_level": "high",
      "confidence": 92.5,
      "finding": "Bone mineral density decreases...",
      "recommendation": "Implement resistance exercise...",
      "supporting_papers": 45
    }
  ]
}
```

### **6. Additional Sources (`sources.json`)**

```json
{
  "total_sources": 1507,
  "sources": [
    {
      "id": "OSDR-001",
      "title": "Biological experiment...",
      "source": "NASA OSDR",
      "type": "Experiment",
      "category": "Biological Sciences",
      "url": "https://osdr.nasa.gov/..."
    }
  ]
}
```

---

## 🚀 **Quick Export Script**

Let me create a script to export all data for Framer:

```python
# export_for_framer.py
import json
import pandas as pd
from pathlib import Path

# Export all data to framer_export/ folder
# Creates JSON files that Framer can fetch
```

---

## 🎨 **Framer Component Examples**

### **Example 1: Paper Card Component**

```tsx
export function PaperCard({ paperId }) {
  const [paper, setPaper] = useState(null);

  useEffect(() => {
    fetch(`/api/papers/${paperId}`)
      .then((res) => res.json())
      .then((data) => setPaper(data));
  }, [paperId]);

  if (!paper) return <div>Loading...</div>;

  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #ddd",
        borderRadius: "8px",
        marginBottom: "16px",
      }}
    >
      <h3>{paper.title}</h3>
      <div style={{ marginTop: "12px" }}>
        <strong>Extractive Summary:</strong>
        <p>{paper.extractive_summary}</p>
      </div>
      <div style={{ marginTop: "12px" }}>
        <strong>Abstractive Summary:</strong>
        <p>{paper.abstractive_summary}</p>
      </div>
      <a href={paper.link} target="_blank">
        View Paper →
      </a>
    </div>
  );
}
```

### **Example 2: Consensus Claims List**

```tsx
export function ConsensusClaims() {
  const [claims, setClaims] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetch("/api/claims")
      .then((res) => res.json())
      .then((data) => setClaims(data.claims));
  }, []);

  const filtered =
    filter === "all" ? claims : claims.filter((c) => c.confidence === filter);

  return (
    <div>
      <h2>Consensus Claims</h2>
      <select onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="strong_consensus">Strong</option>
        <option value="moderate_consensus">Moderate</option>
      </select>

      {filtered.map((claim) => (
        <div
          key={claim.id}
          style={{
            padding: "16px",
            margin: "12px 0",
            background:
              claim.confidence === "strong_consensus" ? "#e8f5e9" : "#fff3e0",
            borderRadius: "8px",
          }}
        >
          <h3>{claim.claim}</h3>
          <div style={{ display: "flex", gap: "16px" }}>
            <span>Confidence: {claim.consensus_score}%</span>
            <span>Supporting: {claim.supporting_papers}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### **Example 3: Topic Explorer**

```tsx
export function TopicExplorer() {
  const [topics, setTopics] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch("/api/topics")
      .then((res) => res.json())
      .then((data) => setTopics(data.topics));
  }, []);

  return (
    <div style={{ display: "flex", gap: "20px" }}>
      {/* Topics List */}
      <div style={{ width: "300px" }}>
        <h3>Research Topics</h3>
        {topics.map((topic, idx) => (
          <button
            key={idx}
            onClick={() => setSelected(topic)}
            style={{
              width: "100%",
              padding: "12px",
              margin: "8px 0",
              textAlign: "left",
              background: selected?.id === topic.id ? "#1976d2" : "#f5f5f5",
              color: selected?.id === topic.id ? "white" : "black",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Topic {topic.id}: {topic.name}
            <br />
            <small>{topic.paper_count} papers</small>
          </button>
        ))}
      </div>

      {/* Topic Details */}
      {selected && (
        <div style={{ flex: 1 }}>
          <h2>
            Topic {selected.id}: {selected.name}
          </h2>
          <p>
            <strong>Keywords:</strong> {selected.keywords.join(", ")}
          </p>
          <p>
            <strong>Papers:</strong> {selected.paper_count}
          </p>

          <h3>Representative Papers</h3>
          {selected.papers_with_titles.slice(0, 5).map((paper) => (
            <div
              key={paper.id}
              style={{
                padding: "12px",
                margin: "8px 0",
                background: "#f5f5f5",
                borderRadius: "4px",
              }}
            >
              <strong>Paper {paper.id}:</strong> {paper.title}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 📦 **What I'll Create Next**

1. **Export Script** - Exports all data to JSON files
2. **FastAPI Server (Optional)** - REST API for dynamic queries
3. **Framer Integration Examples** - Copy-paste components
4. **Data Update Script** - Updates JSON when new papers processed

---

## 🎯 **Recommended Framer Layout**

### **Homepage**

- Hero section with stats (200 papers, 15 claims, etc.)
- Search bar for papers
- Featured topics carousel

### **Papers Page**

- Grid of paper cards
- Filter by topic
- Search functionality

### **Insights Page**

- Consensus claims with confidence scores
- Knowledge gaps visualization
- Mission recommendations

### **Topics Page**

- Interactive topic explorer
- Click topic to see papers
- Keywords and stats

### **Sources Page**

- Browse 1,507 NASA sources
- Filter by type (Mission, Experiment, Project)
- Link to official NASA resources

---

## ✅ **Next Steps**

1. Tell me which integration option you prefer:
   - **Option A:** Simple JSON export for Framer to fetch
   - **Option B:** FastAPI server with REST endpoints
2. Tell me your Framer project structure:

   - Do you have existing components?
   - What design system/colors?
   - What pages do you need?

3. I'll create:
   - Export script
   - Integration code
   - Example Framer components
   - Documentation

**Ready when you are! 🚀**
