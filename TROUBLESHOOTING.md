# Troubleshooting Guide

## Common Issues & Solutions

### 1. ModuleNotFoundError: No module named 'anthropic'

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import anthropic; print(anthropic.__version__)"
```

---

### 2. ANTHROPIC_API_KEY not set

**Cause:** Missing API key in .env

**Solution:**
```bash
cp .env.example .env
# Edit .env and add your key
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**Verify:**
```bash
python -c "from app.config.settings import settings; print(settings.anthropic_api_key[:20])"
```

---

### 3. Address already in use (Port 8000)

**Cause:** Another process using port 8000

**Check:**
```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Solution - Option 1:** Kill the process
```bash
# macOS/Linux
kill -9 <PID>

# Windows
taskkill /PID <PID> /F
```

**Solution - Option 2:** Use different port
```bash
python -m uvicorn app.main:app --port 8001
```

---

### 4. timeout: 30 seconds exceeded

**Cause:** Claude API taking too long or network issues

**Solution:**
```env
# In .env
AGENT_TIMEOUT=60  # Increase from 30
```

**Check internet connection:**
```bash
ping claude.anthropic.com
```

---

### 5. Tavily API Error

**Cause:** Missing or invalid Tavily key

**Solution:**
```bash
# In .env
TAVILY_API_KEY=tvly-xxxxx
```

**If Tavily is down:**
- Fact Checker will gracefully skip
- Analysis continues without web verification

---

### 6. Wikipedia timeout

**Cause:** Wikipedia service slow or unreachable

**Solution:**
```env
# In .env
WIKIPEDIA_TIMEOUT=20  # Increase from 10
```

**Impact:** Fact Checker uses Tavily fallback

---

### 7. CORS Error in Frontend

**Error:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Cause:** Frontend origin not in ALLOWED_ORIGINS

**Solution:**
```env
# In .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://myapp.com
```

**Restart server:**
```bash
Ctrl+C
python -m uvicorn app.main:app --reload
```

---

### 8. JSON Decode Error

**Error:** `json.decoder.JSONDecodeError: Expecting value`

**Cause:** Claude returned invalid JSON

**Solution:**
The system handles this gracefully with fallback parsing. If persistent:

```env
# Lower temperature for more consistent outputs
GENERATOR_TEMPERATURE=0.5
JURY_TEMPERATURE=0.3
```

---

### 9. WebSocket Connection Refused

**Error:** `WebSocket connection to ws://localhost:8000/... failed`

**Cause:** Server not running or incorrect URL

**Check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Fix:** Start the server
```bash
python -m uvicorn app.main:app --reload
```

---

### 10. Memory Issues

**Symptom:** "MemoryError" or very slow responses

**Cause:** Large responses or memory leak

**Solution:**
```bash
# Monitor memory usage
htop  # or Task Manager on Windows

# Restart server
Ctrl+C
python -m uvicorn app.main:app --reload
```

---

## Debug Mode

### Enable Verbose Logging

```env
# In .env
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# Redirect to file
python -m uvicorn app.main:app --reload > juror.log 2>&1

# Watch logs
tail -f juror.log
```

### Debug Agent Responses

Add this to check raw agent outputs:

```python
# In app/agents/generator.py or any agent
logger.debug(f"Raw response: {response_text}")
```

---

## Network Issues

### Check API Connectivity

```bash
# Claude API
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/health

# Tavily API
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_KEY", "query": "test"}'

# Wikipedia
curl "https://en.wikipedia.org/w/api.php?action=query&format=json"
```

---

## Performance Issues

### Slow Responses

**Check execution times:**
```bash
# Look at agent_timings in response
"agent_timings": {
  "Generator": 5.2,  # Too slow?
  "Fact Checker": 8.1,  # Too slow?
  "Math Validator": 0.5,
  "Logic Auditor": 1.2
}
```

**Optimization:**
```env
# Reduce max_results for verification
# Lower temperature for faster generations
GENERATOR_TEMPERATURE=0.5
JURY_TEMPERATURE=0.3
```

### High Memory Usage

```bash
# Check which agent is consuming memory
ps aux | grep uvicorn

# Restart and monitor
python -m uvicorn app.main:app --workers 1
```

---

## Database/Caching Issues

**JUROR doesn't use a database by default.**

To add caching:

```python
# Add to app/services/cache.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cache_analysis(query_hash):
    # Return cached result
    pass
```

---

## Testing the Backend

### Quick Health Check

```bash
curl http://localhost:8000/
```

**Expected:**
```json
{
  "service": "JUROR - AI Hallucination Oversight System",
  "version": "1.0.0",
  "status": "running"
}
```

### Simple Query Test

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Should return:**
- `analysis_id`
- `draft_response`
- `verdict` (PASS/FAIL/PARTIAL)
- Agent results

---

## Getting Help

### Check Logs

```bash
# Real-time logs
tail -f juror.log

# Search for errors
grep ERROR juror.log
```

### Test Individual Agents

```python
# Test generator in isolation
from app.agents.generator import run_generator_agent
import asyncio

result = asyncio.run(run_generator_agent("test query"))
print(result)
```

### Report Issues

Include:
1. Error message
2. Log output
3. Environment (OS, Python version)
4. Query that caused issue
5. .env settings (without secrets)

---

## Still Stuck?

1. Check README.md for architecture overview
2. Review EXAMPLES.md for working code
3. Enable DEBUG logging
4. Check GitHub issues
5. Review Claude API documentation
