# SINASC Dashboard - Deployment Guide

## 🎯 Quick Deploy (Recommended: Render.com)

### Prerequisites
- GitHub account
- This repository pushed to GitHub

### Steps:

1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Render**:
   - Go to https://render.com
   - Sign in with GitHub
   - Click "New +" → "Web Service"
   - Select this repository
   - Render auto-detects Python and uses `render.yaml`
   - Click "Create Web Service"
   - Wait 3-5 minutes ⏰
   - Done! Your dashboard is live 🎉

3. **Access your dashboard**:
   - URL: `https://your-app-name.onrender.com`
   - Free tier includes HTTPS automatically

---

## 🐳 Docker Deployment

### Option 1: Python 3.12 (Maximum Compatibility)
```bash
docker build -t sinasc-dashboard .
docker run -p 8050:8050 sinasc-dashboard
```

### Option 2: Python 3.13 (Latest)
```bash
docker build -f Dockerfile.python313 -t sinasc-dashboard:py313 .
docker run -p 8050:8050 sinasc-dashboard:py313
```

Visit: http://localhost:8050

---

## 🚂 Alternative Platforms

### Railway.app
1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Select repository
4. Auto-deploys using `railway.json`

### Hugging Face Spaces
1. Create account at https://huggingface.co
2. New Space → Dash SDK
3. Upload `dashboard/` and `dashboard_data/`
4. Add `dashboard/requirements.txt`
5. Auto-deploys

---

## 🔧 Local Production Test

Test before deploying:
```bash
cd dashboard
gunicorn app:server --bind 0.0.0.0:8050 --workers 2
```

---

## 📊 Deployment Details

### Python Version
- **Local**: Python 3.13.7 (from UV)
- **Deployment**: Python 3.12.7 (platform compatibility)
- **All packages work on both versions** ✅

### Memory Usage
- Data: ~532KB (excellent!)
- Estimated RAM: <200MB
- Free tier: 512MB (plenty of headroom)

### Performance
- Cold start: ~10s (first request)
- Warm requests: <100ms
- Concurrent users: ~50 on free tier

---

## 🔒 Security Checklist

Before going live:
- [ ] No API keys in code
- [ ] No passwords in git history
- [ ] HTTPS enabled (automatic on Render)
- [ ] Data complies with LGPD
- [ ] `.env` in `.gitignore`

---

## 🆘 Troubleshooting

### Build fails with "Module not found"
- Check `dashboard/requirements.txt` has all dependencies
- Verify package names are correct
- Try: `uv pip freeze > dashboard/requirements.txt`

### App crashes with memory error
- Your data is only 532KB, should be fine
- Check if loading too much data at startup
- Reduce workers: change `--workers 2` to `--workers 1`

### Slow responses
- First request after sleep is slow (free tier)
- Subsequent requests are fast
- Upgrade to paid tier ($7/month) for no sleep

---

## 🎓 Next Steps

1. **Test locally**: `cd dashboard && gunicorn app:server`
2. **Push to GitHub**: `git push`
3. **Deploy to Render**: Follow steps above
4. **Share your dashboard**: Get the URL and share!

---

## 📚 Additional Resources

- [Render.com Docs](https://render.com/docs)
- [Railway.app Docs](https://docs.railway.app)
- [Dash Deployment Guide](https://dash.plotly.com/deployment)
- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Python 3.13 Compatibility](./PYTHON_313_COMPATIBILITY.md)

---

**Questions?** Check DEPLOYMENT_GUIDE.md for detailed information!
