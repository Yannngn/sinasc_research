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



## 🔒 Security Checklist

Before going live:
- [ ] No API keys in code
- [ ] No passwords in git history
- [ ] HTTPS enabled (automatic on Render)
- [ ] Data complies with LGPD
- [ ] `.env` in `.gitignore`

---

## Troubleshooting

**Build fails:**
- Check `dashboard/requirements.txt` has all dependencies
- Try: `uv pip freeze > dashboard/requirements.txt`

**Memory error:**
- Reduce workers: `--workers 1` instead of `--workers 2`

**Slow first request:**
- Free tier sleeps after inactivity
- First request takes ~10s, then fast

---

## Next Steps

1. Test locally: `cd dashboard && gunicorn app:server`
2. Push to GitHub
3. Deploy to Render
4. Share your dashboard!

---

## Resources

- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Render.com Docs](https://render.com/docs)
- [Dash Deployment](https://dash.plotly.com/deployment)
