# 🚀 SINASC Dashboard Deployment Guide

## Overview

Comprehensive deployment options for the SINASC Dashboard.

**Dashboard specs:**
- Data: ~200MB (optimized Parquet files)
- Memory: <200MB RAM estimated
- Stack: Dash + Plotly + Pandas

---

## Recommended Platforms (Ranked)

### 1. ⭐ Render.com (Recommended)

**Pros:**
- Free tier with 512MB RAM
- Auto-deploys from GitHub via `render.yaml`
- HTTPS included
- Custom domains on free tier

**Deployment:**
1. Push code to GitHub
2. Sign in to render.com with GitHub
3. Click "New +" → "Web Service"
4. Select repository
5. Click "Create Web Service" (auto-detects `render.yaml`)

**Cost**: FREE  
**URL**: `https://your-app-name.onrender.com`

---

### 2. Railway.app

**Pros:**
- $5/month initial credit
- Simple GitHub integration
- Automatic HTTPS

**Cons:**
- Requires credit card

**Cost**: Free $5 credit, then ~$3-5/month

---

### 3. Hugging Face Spaces

**Pros:**
- Completely free for public apps
- Great for data science projects
- No credit card required

**Cons:**
- Slower performance
- Manual upload process

**Cost**: FREE

---

### 4. Docker (Self-hosted)

Use the provided `Dockerfile` or `Dockerfile.python313` for containerized deployment on any platform supporting Docker.

---



## Preparation

### Using Deployment Script
```bash
python scripts/prepare_deploy.py
```

This generates:
- `render.yaml` - Render.com config
- `Procfile` - Heroku-style platforms
- `railway.json` - Railway.app config
- `Dockerfile` - Container deployment
- `runtime.txt` - Python version

### Test Locally
```bash
cd dashboard
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

Visit: http://localhost:8050

---

## Security Checklist

- [ ] No API keys in code
- [ ] Environment variables for secrets
- [ ] `.env` in `.gitignore`
- [ ] HTTPS enabled (automatic on Render)
- [ ] LGPD compliance for Brazilian data

---

## Troubleshooting

**Module not found:**
```bash
pip freeze > dashboard/requirements.txt
```

**Memory errors:**
- Reduce workers: change `--workers 2` to `--workers 1`
- Check data loading in callbacks

**Slow startup:**
- First request after sleep (free tier) takes ~10s
- Subsequent requests are fast

---

## Next Steps

1. Run `python scripts/prepare_deploy.py`
2. Push to GitHub
3. Deploy to Render.com
4. Test your live URL

See [DEPLOY_README.md](DEPLOY_README.md) for quick start instructions.
