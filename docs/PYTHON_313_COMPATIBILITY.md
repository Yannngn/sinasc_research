# Python Version Compatibility Guide

## Current Status

**Project**: `requires-python = ">=3.13"` in `pyproject.toml`  
**Deployment**: Python 3.12.7 recommended

## Dashboard Dependencies

All core packages support Python 3.13:

| Package | Version | Python 3.13 |
|---------|---------|-------------|
| dash | 3.2.0+ | ✅ |
| dash-bootstrap-components | 2.0.4+ | ✅ |
| pandas | 2.3.3+ | ✅ |
| pyarrow | 21.0.0+ | ✅ |
| plotly | 6.3.0+ | ✅ |
| gunicorn | 23.0.0+ | ✅ |

## Generate Requirements

```bash
# Export from UV environment
uv pip freeze > dashboard/requirements.txt
```

---

## Platform Support

| Platform | Python 3.13 | Recommendation |
|----------|-------------|----------------|
| Render.com | Partial | Use Python 3.12 |
| Railway.app | Partial | Use Python 3.12 |
| Hugging Face | Partial | Use Python 3.12 |
| Docker | Full | Can use 3.13 |

**Note**: Python 3.13 was released in October 2024. Most platforms are still on 3.12.

---

## Recommended Approach

### Development: Python 3.13 (Optional)
### Deployment: Python 3.12 (Recommended)

**Why Python 3.12 for deployment:**
- Works on all platforms
- Production-stable
- Full package support
- No surprises

**Your code works identically on both versions** - no code changes needed.

---

## Setup for Deployment

1. **Set Python version:**
```bash
echo "python-3.12.7" > runtime.txt
```

2. **Export requirements:**
```bash
uv pip freeze > dashboard/requirements.txt
```

3. **Deploy to Render.com** (supports Python 3.12)

---

## Summary

**Question**: Will my code work with Python 3.13?  
**Answer**: Yes, but use Python 3.12 for deployment.

**Question**: Will I lose features?  
**Answer**: No. Code works identically on 3.12 and 3.13.

**Action**: Use Python 3.12 for deployment, keep 3.13 for local development if desired.
