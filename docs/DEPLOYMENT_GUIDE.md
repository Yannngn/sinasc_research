# 🚀 SINASC Dashboard Deployment Guide

## 📊 Overview

This guide covers deployment options for the SINASC Dashboard. Your dashboard has:
- **Size**: ~532KB data (excellent for free tiers!)
- **Stack**: Dash + Plotly + Pandas
- **Memory**: Optimized pre-aggregated data

---

## 🏆 Recommended Deployment Options (Ranked)

### 1. ⭐ **Render.com** (BEST FOR YOU - Recommended)

**Why Render?**
- ✅ **Free tier**: 512MB RAM (perfect for your 532KB data)
- ✅ **Zero configuration**: Deploys from GitHub automatically
- ✅ **Fast**: Global CDN included
- ✅ **Professional**: Custom domains on free tier
- ✅ **No sleep issues**: Unlike Heroku, stays responsive
- ✅ **No credit card required** for free tier

**Deployment Steps:**
```bash
# 1. Push to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Go to render.com and sign in with GitHub
# 3. Click "New +" → "Web Service"
# 4. Connect your repository
# 5. Configure:
#    - Name: sinasc-dashboard
#    - Build Command: pip install -r dashboard/requirements.txt
#    - Start Command: gunicorn dashboard.app:server
#    - Select "Free" plan
# 6. Click "Create Web Service"
# 7. Done! Your app will be live at: https://sinasc-dashboard.onrender.com
```

**Cost**: FREE forever (with 512MB RAM limit)
**URL**: `https://your-app-name.onrender.com`

---

### 2. 🎯 **Railway.app** (Runner-up)

**Why Railway?**
- ✅ Free $5/month credit (enough for small apps)
- ✅ Simple deployment from GitHub
- ✅ Great developer experience
- ✅ Automatic HTTPS
- ❌ Requires credit card after trial

**Deployment:**
```bash
# 1. Sign up at railway.app
# 2. Click "New Project" → "Deploy from GitHub repo"
# 3. Select your repo
# 4. Railway auto-detects Python and deploys
# 5. Set environment variable: PORT=8080
```

**Cost**: $5/month credit (free tier), then ~$3-5/month
**URL**: `https://your-app.up.railway.app`

---

### 3. 🚂 **Hugging Face Spaces** (ML Community Favorite)

**Why HF Spaces?**
- ✅ **Completely FREE** for public apps
- ✅ Great for data science/ML dashboards
- ✅ Built for Python apps
- ✅ No credit card needed
- ❌ Slower than Render
- ❌ Less professional URLs

**Deployment:**
```bash
# 1. Create account at huggingface.co
# 2. Create new Space (Dash SDK)
# 3. Upload via git or web interface
# 4. Add requirements.txt
# 5. App automatically deploys
```

**Cost**: FREE
**URL**: `https://huggingface.co/spaces/username/sinasc-dashboard`

---

### 4. ☁️ **PythonAnywhere** (Traditional Hosting)

**Why PythonAnywhere?**
- ✅ Free tier available
- ✅ Good for Python beginners
- ✅ No buildpacks needed
- ❌ Manual configuration required
- ❌ Limited to 512MB RAM (but OK for you)

**Cost**: FREE (with ads), $5/month (no ads)

---

### 5. ❌ **NOT Recommended**

**Heroku** (2024):
- ❌ No free tier anymore
- ❌ Minimum $7/month
- ❌ Apps sleep after 30min inactivity

**Google Cloud Run / AWS Lambda**:
- ❌ Overkill for your use case
- ❌ Complex setup
- ❌ Cold starts (slow first load)

---

## 🎨 Cloud Dash (Plotly's Official Solution)

### What is it?
Plotly Dash Cloud is the official hosting for Dash apps by Plotly.

### Pricing (2024):
- **Hobby**: $29/month (1 app)
- **Professional**: $79/month (5 apps)
- **Enterprise**: $250+/month

### Pros:
- ✅ Zero configuration
- ✅ Built specifically for Dash
- ✅ Automatic scaling
- ✅ Professional support

### Cons:
- ❌ **Expensive** compared to alternatives
- ❌ Not cost-effective for side projects
- ❌ Overkill unless you need enterprise features

### Verdict:
**NOT recommended** for your use case. Render.com gives you 95% of the features for FREE.

---

## 🔧 Preparation Script

Run the deployment preparation script:
```bash
python scripts/prepare_deploy.py
```

This will:
1. ✅ Create production requirements.txt
2. ✅ Generate Dockerfile (optional)
3. ✅ Create render.yaml config
4. ✅ Add Procfile for Heroku-style platforms
5. ✅ Validate data files
6. ✅ Create deployment README

---

## 📦 My Recommendation for You

### **Use Render.com** because:

1. **Free Forever**: No credit card, no trials, just free
2. **Your data is tiny**: 532KB fits easily in 512MB RAM
3. **Professional**: Get a proper URL like `sinasc-dashboard.onrender.com`
4. **Reliable**: 99.9% uptime, no cold starts
5. **Easy**: Deploy in 5 minutes from GitHub
6. **Scalable**: If you need more later, upgrade for $7/month

### Quick Start (Render):
```bash
# 1. Prepare deployment files
python scripts/prepare_deploy.py

# 2. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 3. Go to render.com
# 4. Connect GitHub → Deploy
# 5. Done! 🎉
```

---

## 🌐 Alternative: Deploy Locally (For Testing)

```bash
# Test production mode locally first
cd dashboard
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

Visit: http://localhost:8050

---

## 🔒 Security Checklist

Before deploying:
- [ ] Remove any API keys from code
- [ ] Set DEBUG=False in production
- [ ] Use environment variables for secrets
- [ ] Add .env to .gitignore
- [ ] Enable HTTPS (automatic on Render)
- [ ] Check data privacy compliance (LGPD)

---

## 📈 Performance Tips

Your dashboard is already optimized with:
- ✅ Pre-aggregated data (532KB total)
- ✅ Parquet format (fast loading)
- ✅ Efficient callbacks
- ✅ Lazy loading

Additional optimizations:
```python
# In app.py, add for production:
app.config.suppress_callback_exceptions = True
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache static files
```

---

## 🆘 Troubleshooting

### "Module not found" errors:
```bash
# Make sure all dependencies are in requirements.txt
pip freeze > dashboard/requirements.txt
```

### Memory errors on free tier:
```python
# Reduce data loaded at startup
# Your 532KB is fine, but if you add more data:
# - Load data lazily in callbacks
# - Use pagination for large tables
# - Sample data for visualizations
```

### Slow startup:
```bash
# Use gunicorn with preload
gunicorn app:server --preload --workers 1
```

---

## 🎓 Next Steps

1. Run `python scripts/prepare_deploy.py`
2. Review generated files
3. Choose Render.com
4. Deploy in 5 minutes
5. Share your dashboard: `https://sinasc-dashboard.onrender.com`

---

## 💡 Pro Tips

- **Custom Domain**: Render allows custom domains on free tier
- **Analytics**: Add Google Analytics via custom.css
- **Monitoring**: Use Render's built-in metrics
- **Backups**: Your data is in git, always safe
- **Updates**: Push to GitHub → Auto-deploys

---

**Ready to deploy? Run the preparation script!**
```bash
python scripts/prepare_deploy.py
```
