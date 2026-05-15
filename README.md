# 🧑‍⚖️ JUROR — AI Hallucination Oversight System

**A revolutionary multi-agent AI verification system that catches hallucinations in real-time.**

> *Built for the hackathon. Production-ready. Cinematic UX.*

---

## 🎯 What is JUROR?

JUROR is a sophisticated backend that:

1. **Generates** an AI response
2. **Runs a jury of specialized agents** in parallel to verify it
3. **Renders a verdict** (PASS/FAIL/PARTIAL)
4. **Corrects** the response if it fails
5. **Streams live updates** to a beautiful frontend dashboard

### The Problem It Solves

❌ AI hallucinations are unpredictable
❌ Users don't know what to trust
❌ There's no real-time verification layer

✅ JUROR provides **institutional-grade fact-checking** powered by AI

---

## 🏗️ Architecture

```
User Query
    ↓
[GENERATOR AGENT] → Generates initial response
    ↓
┌─────────────────────────────────────────┐
│   PARALLEL JURY EXECUTION (asyncio)     │
├─────────────────────────────────────────┤
│  • Fact Checker (Tavily + Wikipedia)    │
│  • Math Validator (Claude + Logic)      │
│  • Logic Auditor (Reasoning Check)      │
└─────────────────────────────────────────┘
    ↓
[VERDICT AGENT] → Aggregates findings
    ↓
IF FAIL:
  [CORRECTOR AGENT] → Fixes issues
    ↓
[FINAL RESPONSE] → Sent to frontend with:
  • Draft + Corrected response
  • Agent scores & timings
  • Risk assessment
  • Key findings
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | FastAPI + Uvicorn |
| **Language** | Python 3.12+ |
| **Async** | asyncio + concurrent agents |
| **AI** | Claude 3.5 Sonnet (Anthropic) |
| **Verification** | Tavily API + Wikipedia |
| **Real-time** | WebSockets + Server-Sent Events |
| **Type Safety** | Pydantic v2 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- API Keys:
  - `ANTHROPIC_API_KEY` (Claude)
  - `TAVILY_API_KEY` (Search)

### Installation

```bash
# Clone the repo
git clone https://github.com/Devakash1410/juror-backend.git
cd juror-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server is live at:** `http://localhost:8000`

---

## 📡 API Endpoints

### 1. **POST /api/v1/analyze** — Main Analysis

Analyze a query through the complete JUROR pipeline.

**Request:**
```json
{
  "query": "What is the capital of France?",
  "stream_updates": true
}
```

**Response (200 OK):**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What is the capital of France?",
  "draft_response": "The capital of France is Paris...",
  "verdict": "PASS",
  "verdict_confidence": 95.5,
  "risk_level": "LOW",
  "corrected_response": null,
  "generator_result": {
    "agent_name": "Generator",
    "status": "completed",
    "applicable": true,
    "response": "...",
    "confidence": 92,
    "reasoning": "...",
    "execution_time": 2.34
  },
  "fact_checker_result": {
    "agent_name": "Fact Checker",
    "status": "completed",
    "applicable": true,
    "score": 95.0,
    "factual_claims": [...],
    "verified_facts": [...],
    "hallucinations": [],
    "sources_checked": ["Wikipedia", "Tavily"],
    "execution_time": 3.21
  },
  "math_validator_result": {
    "agent_name": "Math Validator",
    "status": "skipped",
    "applicable": false,
    "score": 100,
    "execution_time": 0.15
  },
  "logic_auditor_result": {
    "agent_name": "Logic Auditor",
    "status": "completed",
    "applicable": true,
    "score": 90,
    "execution_time": 1.89
  },
  "verdict_result": {
    "agent_name": "Verdict Agent",
    "status": "completed",
    "verdict": "PASS",
    "confidence": 95.5,
    "risk_level": "LOW",
    "summary": "All jury agents agree...",
    "key_issues": [],
    "jury_breakdown": {
      "fact_check": {"score": 95, "status": "completed"},
      "logic": {"score": 90, "status": "completed"}
    },
    "execution_time": 1.23
  },
  "execution_time": 8.82,
  "agent_timings": {
    "Generator": 2.34,
    "Fact Checker": 3.21,
    "Math Validator": 0.15,
    "Logic Auditor": 1.89,
    "Verdict Agent": 1.23,
    "Corrector": 0
  },
  "jury_consensus_score": 93.5,
  "key_findings": []
}
```

### 2. **GET /api/v1/health** — Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "service": "JUROR Backend",
  "version": "1.0.0"
}
```

### 3. **GET /api/v1/analyses/{analysis_id}** — Retrieve Analysis

```bash
curl http://localhost:8000/api/v1/analyses/550e8400-e29b-41d4-a716-446655440000
```

### 4. **WS /api/v1/ws/jury/{analysis_id}** — Real-time WebSocket

Subscribe to live agent updates during analysis.

**Events:**
```json
{"event_type": "analysis_started", "analysis_id": "..."}
{"event_type": "agent_started", "agent": "Generator"}
{"event_type": "agent_completed", "agent": "Fact Checker", "score": 95}
{"event_type": "verdict_generated", "verdict": "PASS", "confidence": 95.5}
{"event_type": "analysis_completed", "verdict": "PASS", "execution_time": 8.82}
```

### 5. **GET /api/v1/stream/analyze** — Server-Sent Events (SSE)

```bash
curl "http://localhost:8000/api/v1/stream/analyze?query=What%20is%202%2B2"
```

Streams analysis progress as SSE events.

---

## 🧪 Testing from Command Prompt

### Test 1: Simple Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

### Test 2: Math Query (triggers Math Validator)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate: 2^10 + 5^3"}'
```

### Test 3: Fact-Heavy Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the first president of the United States?"}'
```

### Test 4: Logic Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "If A > B and B > C, what can we conclude about A and C?"}'
```

### Test 5: Stream Events

```bash
curl "http://localhost:8000/api/v1/stream/analyze?query=Test%20query"
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# FastAPI
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# API Keys (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# Agent Tuning
AGENT_TIMEOUT=30
GENERATOR_TEMPERATURE=0.7
JURY_TEMPERATURE=0.5
CORRECTOR_TEMPERATURE=0.6
```

---

## 🧠 The Agents

### 1. **Generator Agent**
- **Role:** Create initial response
- **Model:** Claude 3.5 Sonnet
- **Output:** Response + confidence score
- **Status:** 🟢 COMPLETED or 🔴 FAILED

### 2. **Fact Checker Agent**
- **Role:** Verify factual claims
- **Verification:** Tavily API + Wikipedia
- **Detects:** Hallucinations, false claims
- **Smart:** Skips if no factual content
- **Output:** Score (0-100), hallucinations list
- **Status:** 🟢 COMPLETED | 🟡 SKIPPED | 🔴 FAILED

### 3. **Math Validator Agent**
- **Role:** Validate mathematical content
- **Checks:** Formulas, calculations, errors
- **Smart:** Skips if no math detected
- **Output:** Score, errors, corrected formula
- **Status:** 🟢 COMPLETED | 🟡 SKIPPED | 🟠 WARNING | 🔴 FAILED

### 4. **Logic Auditor Agent**
- **Role:** Check logical consistency
- **Checks:** Contradictions, unsupported claims, logic flaws
- **Smart:** Skips if minimal reasoning
- **Output:** Score, issues found
- **Status:** 🟢 COMPLETED | 🟡 SKIPPED | 🟠 WARNING | 🔴 FAILED

### 5. **Verdict Agent**
- **Role:** Aggregate jury findings
- **Verdict Types:**
  - 🟢 **PASS** - All checks pass (confidence ≥80%)
  - 🟡 **PARTIAL** - Some concerns (confidence 60-79%)
  - 🔴 **FAIL** - Major issues (confidence <60%)
- **Output:** Verdict, confidence, risk level, summary

### 6. **Corrector Agent** *(Only runs if FAIL)*
- **Role:** Fix hallucinations and errors
- **Fixes:** All flagged issues
- **Output:** Corrected response + changes made
- **Status:** 🟢 COMPLETED | 🔴 FAILED

---

## 📊 Understanding the Response

### Verdict Meanings

| Verdict | Meaning | Risk | Action |
|---------|---------|------|--------|
| **PASS** | Response is accurate and trustworthy | LOW | Use directly |
| **PARTIAL** | Some concerns but generally acceptable | MEDIUM | Review findings |
| **FAIL** | Major issues detected | HIGH | Use corrected version |

### Agent Status

- **completed** - Agent ran successfully
- **skipped** - Agent not applicable to query
- **warning** - Agent found issues
- **failed** - Agent encountered error

### Scores

- **0-30:** Severe issues ⚠️
- **30-60:** Moderate concerns ⚡
- **60-80:** Generally acceptable ✓
- **80-100:** High confidence ✅

---

## 🎬 Demo Scenarios

### Scenario 1: Hallucination Detection

**Query:** "The Eiffel Tower is in Germany"

**What happens:**
1. Generator creates response
2. Fact Checker detects false claim via Wikipedia
3. Verdict: **FAIL** (confidence: 5%)
4. Corrector fixes to "...is in France"

### Scenario 2: Math Error

**Query:** "What is 2+2?"

**What happens:**
1. Generator says "5" (hypothetically)
2. Math Validator catches error
3. Logic Auditor confirms contradiction
4. Verdict: **FAIL**
5. Corrector fixes to "4"

### Scenario 3: Non-factual Query

**Query:** "What does love mean to you?"

**What happens:**
1. Generator creates thoughtful response
2. Fact Checker: **SKIPPED** (no facts to verify)
3. Math Validator: **SKIPPED** (no math)
4. Logic Auditor: Checks consistency
5. Verdict: **PASS** (if logically sound)

---

## 🔌 WebSocket Usage

### Python Client Example

```python
import asyncio
import websockets
import json

async def monitor_analysis(analysis_id):
    uri = f"ws://localhost:8000/api/v1/ws/jury/{analysis_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            event = await websocket.recv()
            data = json.loads(event)
            print(f"[{data['event_type']}] {data}")

if __name__ == "__main__":
    asyncio.run(monitor_analysis("550e8400-e29b-41d4-a716-446655440000"))
```

### JavaScript Client Example

```javascript
const analysisId = "550e8400-e29b-41d4-a716-446655440000";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/jury/${analysisId}`);

ws.onopen = () => {
    console.log("Connected to JUROR backend");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`[${data.event_type}]`, data);
    
    // Update UI based on event type
    switch(data.event_type) {
        case 'agent_started':
            // Highlight active agent
            break;
        case 'agent_completed':
            // Show score and mark complete
            break;
        case 'verdict_generated':
            // Show verdict card
            break;
    }
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};
```

---

## 🏃 Performance

### Typical Execution Times

| Agent | Time | Notes |
|-------|------|-------|
| Generator | 2-4s | Claude generation |
| Fact Checker | 2-5s | API verification |
| Math Validator | 1-3s | Logic check |
| Logic Auditor | 1-3s | Reasoning analysis |
| Verdict Agent | 1-2s | Aggregation |
| Corrector | 2-4s | Rewrite (if needed) |
| **Total** | **6-15s** | Full pipeline |

**Parallel execution** = Jury agents run simultaneously, not sequentially.

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
# Check your .env file
cat .env | grep ANTHROPIC_API_KEY

# Should output your key
ANTHROPIC_API_KEY=sk-ant-...
```

### Error: "timeout"
```bash
# Increase timeout in .env
AGENT_TIMEOUT=60  # was 30
```

### Error: "Tavily API error"
```bash
# API key might be invalid
# Or Tavily service might be down
# Fact Checker will gracefully degrade
```

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
python -m uvicorn app.main:app --port 8001
```

---

## 📚 Project Structure

```
juror-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config/
│   │   └── settings.py         # Configuration
│   ├── agents/                 # 6 AI agents
│   │   ├── generator.py
│   │   ├── fact_checker.py
│   │   ├── math_validator.py
│   │   ├── logic_auditor.py
│   │   ├── verdict_agent.py
│   │   └── corrector.py
│   ├── services/               # External APIs
│   │   ├── claude_client.py
│   │   ├── tavily_client.py
│   │   └── wikipedia_client.py
│   ├── models/                 # Pydantic schemas
│   │   └── agent_models.py
│   ├── orchestration/
│   │   └── pipeline.py         # Main orchestrator
│   ├── routes/
│   │   └── jury.py            # FastAPI endpoints
│   ├── websocket/
│   │   └── manager.py         # WebSocket mgmt
│   └── utils/                 # Helpers
│       ├── logger.py
│       ├── parser.py
│       ├── scoring.py
│       └── timers.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Railway or Render

1. Push to GitHub
2. Connect repository
3. Set environment variables
4. Deploy

---

## 🤝 Contributing

Fork and submit pull requests! Areas for contribution:
- Additional verification APIs
- Custom agent implementations
- UI improvements
- Performance optimizations

---

## 📄 License

MIT License - Free for hackathons and projects

---

## 🎓 How JUROR Works (Deep Dive)

### The Pipeline Flow

```
1. USER SUBMITS QUERY
   ↓
2. GENERATOR AGENT (Claude)
   - Creates thoughtful response
   - Admits uncertainty
   - Provides confidence score
   ↓
3. PARALLEL JURY EXECUTION (asyncio.gather)
   
   Task 1: FACT CHECKER
   - Extract factual claims
   - Search Tavily + Wikipedia
   - Identify hallucinations
   - Score: 0-100
   
   Task 2: MATH VALIDATOR
   - Detect formulas/calculations
   - Verify using Claude logic
   - Flag errors
   - Score: 0-100
   
   Task 3: LOGIC AUDITOR
   - Check contradictions
   - Verify reasoning chain
   - Find logical fallacies
   - Score: 0-100
   ↓
4. VERDICT AGENT
   - Aggregate jury scores: consensus_score = weighted_average()
   - Determine verdict:
     * PASS (≥80% confidence)
     * PARTIAL (60-79% confidence)
     * FAIL (<60% confidence)
   - Assess risk: LOW/MEDIUM/HIGH
   ↓
5. DECISION: SHOULD WE CORRECT?
   
   IF verdict == FAIL:
   → CORRECTOR AGENT
      - Receives all flagged issues
      - Rewrites response fixing all issues
      - Returns corrected_response
   
   ELSE:
   → Skip corrector
   ↓
6. RESPONSE TO USER
   - Original draft response
   - All agent findings
   - Verdict + confidence
   - Corrected response (if needed)
   - Execution timings
   - Risk assessment
```

### Key Design Decisions

**Why parallel execution?**
- Agents don't depend on each other
- asyncio.gather() runs 3 agents concurrently
- Reduces total latency significantly

**Why context-aware agents?**
- Fact Checker skips if no facts to verify
- Math Validator skips if no math detected
- Logic Auditor skips if minimal reasoning
- Prevents meaningless false positives

**Why jury consensus?**
- No single agent is 100% reliable
- Weighted scoring prevents ties
- Fact Check: 40% (most critical)
- Math: 35% (critical for technical queries)
- Logic: 25% (supports other findings)

---

## 🎯 Use Cases

1. **Educational Platforms** - Verify AI tutor responses
2. **Content Generation** - Check blog/article AI drafts
3. **Customer Support** - Validate AI chatbot answers
4. **Research** - Fact-check AI literature summaries
5. **Finance** - Verify AI market analysis
6. **Medical** - Ensure accuracy of health info
7. **Legal** - Check AI contract analysis

---

## 💡 Future Enhancements

- [ ] Custom agent injections
- [ ] Multi-modal verification (images, video)
- [ ] Hallucination severity scoring
- [ ] Confidence calibration over time
- [ ] Agent voting system
- [ ] Adversarial testing mode
- [ ] Custom prompt templates
- [ ] Response caching
- [ ] Rate limiting
- [ ] Analytics dashboard

---

## 📞 Support

- **Issues:** GitHub Issues
- **Email:** support@juror.ai
- **Discord:** [Coming soon]

---

**Built with ❤️ for the hackathon. Ship it! 🚀**
