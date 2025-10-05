# 🚀 Deploy & Embed Guide - Get Your Dashboard into Framer

## ✅ What I Just Fixed

Your knowledge graph now has:

- **Dark blue background** (#1a1f2e) - visible, not pitch black
- **Blue/white theme** - perfect for Framer
- **Better spacing** (k=5.5, 200 iterations) - no overlaps
- **More visible lines** (1.5px width, clearer blue)
- **Simple, clean design** - not overly complex
- **Defined shapes** with white borders

## 🎯 Step-by-Step: Deploy to Streamlit Cloud

### **Step 1: Prepare Your Repository**

First, make sure your code is committed to GitHub:

```bash
cd /Applications/SpaceAppsHackatho/spaceapps-data-parsing

# Check current status
git status

# Add all changes
git add .

# Commit with a message
git commit -m "Final dashboard with knowledge graph ready for deployment"

# Push to GitHub
git push origin main
```

### **Step 2: Sign Up for Streamlit Cloud**

1. Go to **https://share.streamlit.io/**
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit to access your GitHub account
4. You'll be redirected to your Streamlit Cloud dashboard

### **Step 3: Deploy Your App**

1. Click **"New app"** button
2. Fill in the deployment form:

   - **Repository**: Select your `spaceapps-data-parsing` repo
   - **Branch**: `main`
   - **Main file path**: `dashboard_complete.py`
   - **App URL**: Choose a custom URL (e.g., `nasa-bioscience-explorer`)

3. Click **"Advanced settings"** (optional but recommended):

   - **Python version**: 3.9 or later
   - **Secrets**: (none needed for now)

4. Click **"Deploy!"**

### **Step 4: Wait for Deployment**

- Deployment takes 3-5 minutes
- You'll see logs showing the build process
- Once done, you'll get a URL like: `https://nasa-bioscience-explorer.streamlit.app/`

## 🔗 Step-by-Step: Embed in Framer

### **Method 1: iframe Embed (Recommended)**

1. **Copy your Streamlit app URL** (e.g., `https://your-app.streamlit.app/`)

2. **In Framer:**

   - Add an **iframe** component to your page
   - Or use an **Embed** component
   - Set the source URL to your Streamlit app

3. **Framer Code:**

```jsx
<iframe
  src="https://your-app.streamlit.app/"
  width="100%"
  height="900px"
  frameborder="0"
  style={{ border: "none" }}
/>
```

### **Method 2: Embed Specific Tab**

To embed ONLY the Knowledge Graph tab:

```jsx
<iframe
  src="https://your-app.streamlit.app/?page=Knowledge+Graph"
  width="100%"
  height="900px"
  frameborder="0"
/>
```

### **Method 3: Full-Width Responsive Embed**

For a responsive embed that fits your Framer design:

```jsx
<div
  style={{
    position: "relative",
    width: "100%",
    paddingBottom: "56.25%", // 16:9 aspect ratio
    height: 0,
    overflow: "hidden",
  }}
>
  <iframe
    src="https://your-app.streamlit.app/"
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      border: "none",
    }}
  />
</div>
```

## 🎨 Styling for Framer Integration

Your dashboard now uses a **blue/black/white theme** that matches well with most designs:

- **Background**: Dark blue (#1a1f2e)
- **Text**: White
- **Nodes**: Blue shades (#4A90E2, #0066CC, #87CEEB, #1E90FF)
- **Lines**: Blue with transparency
- **Borders**: White

### To Hide Streamlit UI Elements (optional):

Add this to your Framer embed URL:

```
https://your-app.streamlit.app/?embedded=true
```

Or use Streamlit's query parameters:

```
?embed=true&embed_options=show_toolbar,show_padding,show_footer
```

## 🛠️ Alternative: Deploy to Vercel/Netlify (if needed)

If Streamlit Cloud doesn't work, you can containerize and deploy elsewhere:

### Option A: Using Docker

1. Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard_complete.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Deploy to Railway/Render/Fly.io

### Option B: Export to Static HTML (Limited)

For static sections only (not the full interactive app):

```bash
# This won't work for the full app, but for reference
streamlit run dashboard_complete.py --server.headless=true
```

## 📋 Checklist Before Deploying

- [ ] Code committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] All data files are in the repository
- [ ] Dashboard runs locally without errors
- [ ] Knowledge graph looks good with blue/white theme
- [ ] No hardcoded local paths in code

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError" during deployment

**Solution**: Make sure all imports are in `requirements.txt`

### Issue: "File not found" errors

**Solution**: Check that all data files (CSV, JSON) are committed to GitHub

### Issue: App is slow or times out

**Solution**: Consider reducing data size or using data caching

### Issue: Embed shows scrollbars

**Solution**: Set iframe height to 900px or use responsive container

### Issue: Can't see the Knowledge Graph tab

**Solution**: Make sure you navigate to it or use the direct URL parameter

## 🎯 For Your Hackathon Presentation

### **Live URL to Share:**

Once deployed, you'll have a URL like:

```
https://nasa-bioscience-explorer.streamlit.app/
```

### **QR Code (optional):**

Generate a QR code pointing to your live app so judges can access it easily

### **Embed in Framer:**

Your Framer site will show the full dashboard embedded seamlessly

## 📊 Performance Tips for Framer

1. **Use lazy loading**: Load the iframe only when visible
2. **Set proper dimensions**: 900px height works well
3. **Preload critical data**: Ensure fast initial load
4. **Test on mobile**: Make sure it's responsive

## 🔄 Quick Deploy Commands

Here's the complete sequence to deploy:

```bash
# 1. Make sure everything is committed
cd /Applications/SpaceAppsHackatho/spaceapps-data-parsing
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to https://share.streamlit.io/
# 3. Click "New app"
# 4. Select your repo and dashboard_complete.py
# 5. Click "Deploy"
# 6. Wait 3-5 minutes
# 7. Copy your URL

# 8. In Framer, add embed code:
# <iframe src="YOUR_URL" width="100%" height="900px" />
```

## 🎉 You're Almost There!

Once you complete these steps:

1. Your dashboard will be **live on the internet**
2. **Anyone can access it** via the URL
3. It will be **embedded in your Framer site**
4. Perfect for your **hackathon presentation**

## 📞 Need Help?

If you run into issues:

1. Check Streamlit Cloud logs
2. Verify all files are committed
3. Test locally first: `streamlit run dashboard_complete.py`
4. Check that data files exist

---

**Ready to deploy? Let's get your dashboard live!** 🚀

Run the git commands above, then go to https://share.streamlit.io/ and follow the steps!
