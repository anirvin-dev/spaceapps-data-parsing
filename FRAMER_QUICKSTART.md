# 🚀 Framer Quick Start - 5 Minutes to Integration

## 📦 **Step 1: Copy Data (1 minute)**

### **From This Project:**

```
/Applications/SpaceAppsHackatho/spaceapps-data-parsing/framer_export/
```

### **To Your Framer Project:**

```
your-framer-project/public/api/
```

**Copy these 7 files:**

1. `papers.json` (368 KB)
2. `claims.json` (15 KB)
3. `topics.json` (3 KB)
4. `gaps.json` (3 KB)
5. `insights.json` (3 KB)
6. `sources.json` (551 KB)
7. `stats.json` (0.2 KB)

**Total:** ~940 KB

---

## 🎨 **Step 2: Create Basic Component (2 minutes)**

### **Create: `PapersList.tsx` in Framer**

```typescript
import { useState, useEffect } from "react";

export function PapersList() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => {
        setPapers(data.papers.filter((p) => p.has_summary));
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading papers...</div>;

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>NASA Research Papers ({papers.length})</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        {papers.map((paper) => (
          <div
            key={paper.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "20px",
              backgroundColor: "white",
            }}
          >
            <h3 style={{ fontSize: "18px", marginBottom: "10px" }}>
              {paper.title}
            </h3>

            <div style={{ marginTop: "15px" }}>
              <strong>Summary:</strong>
              <p style={{ marginTop: "8px", color: "#555", fontSize: "14px" }}>
                {paper.abstractive_summary}
              </p>
            </div>

            <a
              href={paper.link}
              target="_blank"
              style={{
                display: "inline-block",
                marginTop: "15px",
                color: "#1976d2",
                textDecoration: "none",
              }}
            >
              Read Full Paper →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 📊 **Step 3: Add Stats Dashboard (2 minutes)**

### **Create: `StatsOverview.tsx`**

```typescript
import { useState, useEffect } from "react";

export function StatsOverview() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch("/api/stats.json")
      .then((res) => res.json())
      .then((data) => setStats(data));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: "20px",
        padding: "40px",
      }}
    >
      <StatCard
        title="Papers"
        value={stats.papers_with_summaries}
        subtitle="with AI summaries"
        color="#1976d2"
      />
      <StatCard
        title="Consensus Claims"
        value={stats.consensus_claims}
        subtitle="evidence-backed"
        color="#388e3c"
      />
      <StatCard
        title="NASA Sources"
        value={stats.additional_sources}
        subtitle="integrated"
        color="#f57c00"
      />
      <StatCard
        title="Total Data"
        value={stats.total_data_points}
        subtitle="sources analyzed"
        color="#7b1fa2"
      />
    </div>
  );
}

function StatCard({ title, value, subtitle, color }) {
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
      <h3 style={{ fontSize: "16px", opacity: 0.9, marginBottom: "10px" }}>
        {title}
      </h3>
      <div
        style={{ fontSize: "48px", fontWeight: "bold", marginBottom: "5px" }}
      >
        {value}
      </div>
      <div style={{ fontSize: "14px", opacity: 0.9 }}>{subtitle}</div>
    </div>
  );
}
```

---

## 🔍 **Step 4: Add Search (Bonus)**

### **Enhance PapersList with Search:**

```typescript
export function PapersList() {
  const [papers, setPapers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => {
        setPapers(data.papers.filter((p) => p.has_summary));
        setLoading(false);
      });
  }, []);

  // Filter papers by search
  const filtered = papers.filter(
    (p) =>
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.abstractive_summary.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div>Loading papers...</div>;

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>NASA Research Papers ({filtered.length})</h1>

      {/* Search Bar */}
      <input
        type="text"
        placeholder="Search papers..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          width: "100%",
          padding: "15px",
          fontSize: "16px",
          border: "2px solid #ddd",
          borderRadius: "8px",
          marginTop: "20px",
          marginBottom: "30px",
        }}
      />

      {/* Papers Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
          gap: "20px",
        }}
      >
        {filtered.map((paper) => (
          <PaperCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
}
```

---

## 🎯 **What You Can Build**

### **5 Core Pages:**

1. **Home** - Stats + Featured Papers
2. **Papers** - All 200 with search/filter
3. **Topics** - 10 topics with source papers
4. **Insights** - Claims, Gaps, Mission Insights
5. **Sources** - 1,507 NASA missions/experiments

### **Each Takes ~15 Minutes to Build**

---

## 📱 **Responsive Design Tips**

```typescript
// Use CSS Grid for responsive layout
style={{
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
  gap: "20px"
}}

// Stack on mobile
@media (max-width: 768px) {
  gridTemplateColumns: "1fr";
}
```

---

## 🎨 **Match Your Design System**

### **Replace inline styles with your Framer design tokens:**

```typescript
// Instead of:
style={{ color: "#1976d2" }}

// Use your design system:
style={{ color: theme.colors.primary }}
```

---

## ✅ **Checklist**

### **Before You Start:**

- [ ] JSON files copied to Framer project
- [ ] Verified files load at `/api/*.json`

### **Build Order:**

1. [ ] Stats overview (easiest)
2. [ ] Papers list (core feature)
3. [ ] Search functionality
4. [ ] Topics explorer
5. [ ] Claims/Insights pages

### **Polish:**

- [ ] Add loading states
- [ ] Add error handling
- [ ] Style to match design
- [ ] Test on mobile
- [ ] Add animations (optional)

---

## 🚀 **Deploy Checklist**

### **Before Demo:**

- [ ] All JSON files in production build
- [ ] Test all fetch calls work
- [ ] Verify links open correctly
- [ ] Test search functionality
- [ ] Check mobile responsiveness

---

## 💡 **Pro Tips**

### **1. Use Custom Hooks**

```typescript
// Create: useData.ts
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

// Use everywhere:
const { papers, loading } = usePapers();
```

### **2. Cache Data**

```typescript
// Add to localStorage
useEffect(() => {
  const cached = localStorage.getItem("papers");
  if (cached) {
    setPapers(JSON.parse(cached));
    setLoading(false);
  } else {
    fetch("/api/papers.json")
      .then((res) => res.json())
      .then((data) => {
        setPapers(data.papers);
        localStorage.setItem("papers", JSON.stringify(data.papers));
        setLoading(false);
      });
  }
}, []);
```

### **3. Lazy Load**

```typescript
// Only load data when component mounts
const [showPapers, setShowPapers] = useState(false);

return (
  <div>
    <button onClick={() => setShowPapers(true)}>Show Papers</button>
    {showPapers && <PapersList />}
  </div>
);
```

---

## 📞 **Need Help?**

### **Common Issues:**

**"404 Not Found" when fetching JSON:**

- Check files are in `/public/api/` or correct location
- Verify path starts with `/api/` not `./api/`

**"CORS Error":**

- JSON files must be served from same domain
- In development, use Framer's built-in server

**"Component Not Updating":**

- Check useState/useEffect are called at top level
- Verify fetch is inside useEffect

---

## 🎯 **Bottom Line**

**5 Minutes:**

- Copy 7 JSON files (940 KB)
- Create basic component
- Display papers

**30 Minutes:**

- All 5 pages working
- Search + filters
- Styled to match design

**1 Hour:**

- Polished UI
- Animations
- Mobile responsive
- Production ready

**READY TO BUILD! 🚀**
