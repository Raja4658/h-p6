# Vercel Deployment Guide (Optimized)

## Prerequisites

1. **HuggingFace Account & API Token**
   - Go to https://huggingface.co/settings/tokens
   - Create a new token (can be read-only)
   - Copy the token

2. **Vercel Account**
   - Sign up at https://vercel.com
   - Connect your GitHub repository

## Setup for Vercel

### Step 1: Set Environment Variable

In your Vercel project dashboard:
1. Go to **Settings** → **Environment Variables**
2. Add new variable:
   - **Name**: `HUGGINGFACE_API_TOKEN`
   - **Value**: Your HF token from step 1
3. Click **Save**

### Step 2: Deploy

**Option A: Manual Deploy**
```bash
git add .
git commit -m "Optimized for Vercel deployment"
git push origin main
```

Vercel auto-detects push and deploys automatically.

**Option B: Vercel CLI**
```bash
npm install -g vercel
vercel
```

### Step 3: Verify Deployment

Once deployed:
1. Get your Vercel URL (e.g., `https://h-p6.vercel.app`)
2. Test health endpoint:
   ```bash
   curl https://h-p6.vercel.app/api/v1/health
   ```

3. Test evaluation:
   ```bash
   curl -X POST https://h-p6.vercel.app/api/v1/evaluate \
     -H "Content-Type: application/json" \
     -d '{
       "submission_id": "test_1",
       "question_id": "q1",
       "answer_text": "Supervised learning uses labeled data.",
       "rubric_id": "r1"
     }'
   ```

## How It Works on Vercel

- **Local Machine**: Uses local `torch` + `transformers` (full setup in `requirements.txt`)
- **Vercel**: Uses HuggingFace Inference API (lightweight `requirements-vercel.txt`)
- **Duplicate Detection**: 
  - Local: SentenceTransformers embeddings
  - Vercel: Simple string matching (fallback)

## Important Notes

1. **Streamlit Dashboard**: Not available on Vercel (serverless limitation)
   - Only FastAPI backend is deployed
   - Use local/Docker for full stack with Streamlit

2. **First Request Timeout**: Initial request may take 10-15 seconds (model warming up)
   - Subsequent requests are faster

3. **API Rate Limits**: Free HuggingFace tier has rate limits
   - Use paid tier for production

4. **HUGGINGFACE_API_TOKEN**: Required for Vercel deployment
   - Must be set in environment variables
   - Otherwise, inference will fail

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if `HUGGINGFACE_API_TOKEN` is set in Vercel |
| 500 Internal Error | Check Vercel logs: `vercel logs` |
| Timeout errors | HF API is slow, try increasing timeout |
| Import errors | Make sure all imports in code have fallbacks |

## Switching Between Environments

**For Local Development:**
```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**For Vercel Deployment:**
- Push to GitHub
- Vercel uses `vercel.json` which specifies `requirements-vercel.txt`
- Must set `HUGGINGFACE_API_TOKEN` in Vercel environment

## Fallback Mechanism

If packages are missing on Vercel:

1. **ai_engine.py**: Falls back to HuggingFace API
2. **duplicate_checker.py**: Falls back to simple string matching
3. **main.py**: Same API routes, same behavior

From the user's perspective, everything works the same!

## Next Steps

1. Set `HUGGINGFACE_API_TOKEN` in Vercel dashboard
2. Push code to GitHub
3. Vercel deploys automatically
4. Test your API endpoints
5. Scale up HF API tier as needed for production
