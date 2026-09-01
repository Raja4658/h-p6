# Deployment Guide

## ⚡ RECOMMENDED: Railway.app or Render.com (FREE, No Errors)

Your existing Docker setup works perfectly on Railway/Render. No bundle size issues, no Vercel errors!

### Railway.app (Simplest - 2 Minutes)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"  
3. Select your repository
4. Railway auto-detects Docker → **Deploy!** ✅
5. Get your public URL instantly

### Render.com (Also Great)
1. Go to https://render.com
2. "New +" → "Web Service"
3. Connect GitHub
4. Deploy with Docker → Done! ✅

**Both support:**
- ✅ Full Docker (no size limits)
- ✅ torch + transformers + all dependencies
- ✅ Free tier with 750 hours/month
- ✅ Auto-redeploy on git push
- ✅ Custom domains

See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for step-by-step guide.

---

## Option 1: Docker (Local or Cloud)

### Prerequisites
- Docker installed on your machine

### Deploy Locally with Docker

```bash
# Build the Docker image
docker build -t auto-grader-api .

# Run the container
docker run -p 8000:8000 -p 8501:8501 auto-grader-api
```

The API will be available at:
- **FastAPI Backend**: http://localhost:8000
- **Streamlit Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/api/v1/health
- **API Docs**: http://localhost:8000/docs

### Or use Docker Compose

```bash
docker compose up --build
```

---

## Option 2: Local Python Setup

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Install & Run

**Windows (PowerShell):**
```powershell
.\run.ps1
```

**Linux/macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Manual:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run API server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, run dashboard (optional)
streamlit run dashboard.py --server.port 8501
```

---

## Option 3: Vercel (Advanced - Lightweight Mode)

**⚠️ Note:** Vercel has 500MB bundle limit. Your full setup with torch/transformers is 5GB+.

### Solution: Use HuggingFace Inference API instead

1. Get free HF API token: https://huggingface.co/settings/tokens
2. In Vercel Environment Variables, set: `HUGGINGFACE_API_TOKEN=hf_xxxxx`
3. Update `main.py` to use `ai_engine_vercel.py`
4. Use lightweight requirements:
   ```bash
   pip install -r requirements-vercel.txt
   ```

**But honestly, Railway/Render are better. Use those instead!** 🚀

---

## Testing the Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Evaluate answer
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": "sub_1",
    "question_id": "q1",
    "answer_text": "Supervised learning is a machine learning method where models are trained using labeled data.",
    "rubric_id": "r1"
  }'
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| Port 8000 already in use | `lsof -i :8000` then `kill -9 <PID>` (Mac/Linux) or `.\run.ps1` (Windows) |
| docker-compose not found | Use `docker compose up` instead (newer Docker Desktop) |
| torch installation fails | Use Docker or Railway instead (Vercel doesn't work with torch) |
| Models fail to download | Check internet connection, HF rate limits |
| Permission denied on Windows | Run PowerShell as Administrator or use `.\run.ps1` |
| Streamlit won't connect | Try different port: `streamlit run dashboard.py --server.port 8502` |

---

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Docker builds successfully: `docker build -t test .`
- [ ] API starts: `python -m uvicorn main:app --reload`
- [ ] Health check passes: `curl http://localhost:8000/api/v1/health`
- [ ] Evaluation endpoint works
- [ ] Dashboard loads (optional)
- [ ] Choose deployment platform
- [ ] Deploy and test!



