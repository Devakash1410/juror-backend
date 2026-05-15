# Complete Setup Guide

## Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/))
- **API Keys:**
  - Anthropic Claude API key
  - Tavily API key (optional but recommended)

## Step 1: Clone Repository

```bash
git clone https://github.com/Devakash1410/juror-backend.git
cd juror-backend
```

## Step 2: Create Virtual Environment

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```cmd
python -m venv venv
venv\Scripts\activate
```

**Verify activation:** Prompt should show `(venv)` prefix

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify installation:**
```bash
pip list | grep fastapi
pip list | grep anthropic
```

## Step 4: Configure Environment

### Create .env file

```bash
cp .env.example .env
```

### Get API Keys

#### Anthropic Claude

1. Go to https://console.anthropic.com/
2. Sign up or login
3. Create API key
4. Copy key

#### Tavily Search (Optional)

1. Go to https://tavily.com/
2. Sign up
3. Get API key
4. Copy key

### Edit .env

```bash
# Using nano
nano .env

# Using vim
vim .env

# Using VS Code
code .env
```

**Required:**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

**Optional tweaks:**
```env
DEBUG=true
LOG_LEVEL=INFO
AGENT_TIMEOUT=30
```

## Step 5: Run the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Server is now live at:**
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Step 6: Verify Installation

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "JUROR Backend",
  "version": "1.0.0"
}
```

### Test Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

**Expected:** Full analysis response with PASS/FAIL verdict

## Step 7: Access Documentation

### Interactive API Docs

Open in browser:
```
http://localhost:8000/docs
```

This shows:
- All endpoints
- Request/response schemas
- Try it out feature
- Authentication details

## Next Steps

### For Development

1. Read EXAMPLES.md for API usage
2. Review architecture in README.md
3. Check TROUBLESHOOTING.md for common issues

### For Frontend Integration

1. Configure CORS in .env:
   ```env
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```
2. Restart server
3. Frontend can now call the API

### For Production

1. Set `ENVIRONMENT=production`
2. Set `DEBUG=false`
3. Use Gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
4. Deploy to Render, Railway, or self-hosted

## Troubleshooting

### Python not found

```bash
# Check installation
python --version
python3 --version

# Use python3 if python doesn't work
python3 -m venv venv
```

### Pip not found

```bash
# Ensure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Try pip3
pip3 install -r requirements.txt
```

### Port 8000 in use

```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or kill the process
lsof -i :8000
kill -9 <PID>
```

### API key errors

1. Verify .env file has correct keys
2. Check no extra spaces around =
3. Verify keys are not expired
4. Test keys independently

## File Structure After Setup

```
juror-backend/
├── venv/                    # Virtual environment
├── app/                     # Application code
├── requirements.txt         # Dependencies
├── .env                     # Configuration (created)
├── .env.example            # Template
├── README.md               # Documentation
├── SETUP.md                # This file
├── EXAMPLES.md             # API examples
└── TROUBLESHOOTING.md      # Help guide
```

## Quick Reference

### Start Server
```bash
source venv/bin/activate  # Activate venv
python -m uvicorn app.main:app --reload
```

### Stop Server
```bash
Ctrl+C
```

### Deactivate venv
```bash
deactivate
```

### Test API
```bash
curl http://localhost:8000/api/v1/health
```

### View Logs
```bash
# If redirected to file
tail -f juror.log
```

## Environment Variables Reference

| Variable | Default | Notes |
|----------|---------|-------|
| `ENVIRONMENT` | development | Set to production for deployment |
| `DEBUG` | true | Set to false in production |
| `API_PORT` | 8000 | Port to run on |
| `ANTHROPIC_API_KEY` | required | Get from console.anthropic.com |
| `TAVILY_API_KEY` | optional | Get from tavily.com |
| `AGENT_TIMEOUT` | 30 | Seconds before timeout |
| `LOG_LEVEL` | INFO | DEBUG/INFO/WARNING/ERROR |

## Getting API Keys

### Anthropic Claude

1. Visit https://console.anthropic.com/
2. Click "Create API key"
3. Copy the key starting with `sk-ant-`
4. Add to .env

### Tavily

1. Visit https://tavily.com/
2. Sign up
3. Go to dashboard
4. Copy API key
5. Add to .env

## Verifying Everything Works

### Step-by-step verification

```bash
# 1. Verify venv is active
which python  # Should show path in venv/

# 2. Verify dependencies
python -c "import fastapi; print(fastapi.__version__)"

# 3. Verify config
python -c "from app.config.settings import settings; print(settings.environment)"

# 4. Start server
python -m uvicorn app.main:app --reload

# In another terminal:
# 5. Test health
curl http://localhost:8000/api/v1/health

# 6. Test analysis
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## Success!

✅ Backend is running
✅ API is responsive
✅ Agents are working
✅ Ready for frontend integration

Next: Check README.md for API documentation or EXAMPLES.md for sample code.
