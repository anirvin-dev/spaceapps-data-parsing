# ⚡ Quick Start: Embed in Framer (5 Minutes)

## Current Status ✅

Your knowledge graph is now **perfect for embedding**:

- ✅ Dark blue background (not pitch black, clearly visible)
- ✅ Blue/black/white theme
- ✅ Proper spacing (no overlaps)
- ✅ Visible connection lines
- ✅ Clean, simple design
- ✅ Well-defined shapes with white borders

## 🚀 3-Step Deployment

### **Step 1: Push to GitHub (2 minutes)**

```bash
cd /Applications/SpaceAppsHackatho/spaceapps-data-parsing
git add .
git commit -m "Dashboard ready for Framer embedding"
git push origin main
```

### **Step 2: Deploy to Streamlit Cloud (3 minutes)**

1. Go to: **https://share.streamlit.io/**
2. Click **"Sign in with GitHub"**
3. Click **"New app"**
4. Select:
   - Repository: `spaceapps-data-parsing`
   - Branch: `main`
   - Main file: `dashboard_complete.py`
5. Click **"Deploy!"**
6. Wait 3-5 minutes
7. **Copy your URL** (e.g., `https://your-app.streamlit.app/`)

### **Step 3: Embed in Framer (1 minute)**

#### Option A: Embed Entire Dashboard

In Framer, add this code to an embed or code component:

```html
<iframe
  src="https://YOUR-APP-URL.streamlit.app/"
  width="100%"
  height="900px"
  style="border: none; border-radius: 8px;"
  allowfullscreen
></iframe>
```

#### Option B: Embed ONLY Knowledge Graph

```html
<iframe
  src="https://YOUR-APP-URL.streamlit.app/?page=🕸️+Knowledge+Graph"
  width="100%"
  height="900px"
  style="border: none; border-radius: 8px;"
></iframe>
```

#### Option C: Responsive Full-Width

```html
<div style="position: relative; width: 100%; padding-bottom: 75%; height: 0;">
  <iframe
    src="https://YOUR-APP-URL.streamlit.app/"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
  ></iframe>
</div>
```

## 🎨 Framer Integration Tips

### In Framer's Code Component:

```typescript
export default function StreamlitEmbed() {
  return (
    <div
      style={{
        width: "100%",
        height: "900px",
        borderRadius: "12px",
        overflow: "hidden",
        boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
      }}
    >
      <iframe
        src="https://YOUR-APP-URL.streamlit.app/"
        width="100%"
        height="100%"
        style={{ border: "none" }}
      />
    </div>
  );
}
```

### For Framer Motion Component:

```typescript
import { motion } from "framer-motion";

export default function DashboardSection() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <iframe
        src="https://YOUR-APP-URL.streamlit.app/"
        width="100%"
        height="900px"
        style={{ border: "none", borderRadius: "8px" }}
      />
    </motion.div>
  );
}
```

## 📱 Responsive Design

### For Mobile-Friendly Embedding:

```html
<div
  style="
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
"
>
  <iframe
    src="https://YOUR-APP-URL.streamlit.app/"
    width="100%"
    height="900px"
    style="
      border: none;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    "
  ></iframe>
</div>
```

### For Different Screen Sizes in Framer:

```typescript
export default function ResponsiveDashboard() {
  const isMobile = window.innerWidth < 768;

  return (
    <iframe
      src="https://YOUR-APP-URL.streamlit.app/"
      width="100%"
      height={isMobile ? "600px" : "900px"}
      style={{ border: "none" }}
    />
  );
}
```

## 🎯 What Judges Will See

When you present:

1. Your **Framer site** loads
2. The embedded **Streamlit dashboard** appears seamlessly
3. They can **interact** with the knowledge graph
4. All **9 tabs** are accessible
5. **Professional, clean design** with blue/white theme

## 🔧 Troubleshooting

### If embed doesn't show:

1. Check that your Streamlit app is deployed and accessible
2. Verify the iframe source URL is correct
3. Check browser console for any errors
4. Make sure Framer allows iframe embeds

### If it's too small/large:

1. Adjust the `height` property (try 700px, 800px, 900px, 1000px)
2. Use responsive wrapper for better fit
3. Test on different screen sizes

### If colors don't match:

1. The dashboard uses dark blue (#1a1f2e) background
2. You can wrap it in a container with matching background
3. Add padding/margin for spacing

## 📊 Recommended Framer Layout

```
┌─────────────────────────────────────┐
│  Hero Section                        │
│  (Your NASA Bioscience Intro)        │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  📊 Interactive Dashboard            │
│  [Streamlit Embed Here]             │
│  - Overview                          │
│  - Knowledge Graph                   │
│  - All 9 tabs accessible             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  About / Team Section                │
└─────────────────────────────────────┘
```

## ⚡ Express Deployment (For Hackathon)

**If you're in a rush:**

1. **GitHub**:

   ```bash
   git add . && git commit -m "deploy" && git push
   ```

2. **Streamlit Cloud**:

   - https://share.streamlit.io/ → New app → Deploy

3. **Framer**:
   ```html
   <iframe
     src="YOUR_URL"
     width="100%"
     height="900px"
     style="border:none"
   ></iframe>
   ```

**Done!** 🎉

## 🎪 Demo Tips

### For Judges:

1. Show the **Framer site** first (professional landing page)
2. Scroll to the **embedded dashboard**
3. Navigate to **Knowledge Graph tab**
4. **Interact** with the graph (hover, zoom, filter)
5. Show **other tabs** (1507 sources, topics, etc.)

### Backup Plan:

Keep the direct Streamlit URL handy:

- If embed has issues, open in new tab
- Still shows the same content
- Judges can interact directly

## 📋 Pre-Presentation Checklist

- [ ] Dashboard deployed to Streamlit Cloud
- [ ] Got the live URL
- [ ] Tested the URL in browser
- [ ] Embedded in Framer
- [ ] Tested embed in Framer preview
- [ ] Knowledge graph looks good (blue/white theme)
- [ ] All tabs accessible
- [ ] Mobile responsive (if needed)
- [ ] Backup URL ready

## 🎉 You're Ready!

Your dashboard has:

- ✅ **Clean design** with blue/black/white theme
- ✅ **Proper spacing** (no overlapping nodes)
- ✅ **Visible connections** (clear lines)
- ✅ **Simple, professional** appearance
- ✅ **Perfect for Framer embedding**

Now just deploy and embed! 🚀

---

**Questions?** Just ask! I'm here to help you get this live for your hackathon presentation! 🎪
