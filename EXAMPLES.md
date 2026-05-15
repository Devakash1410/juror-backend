# JUROR API Examples

## Complete cURL Examples

### 1. Basic Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?",
    "stream_updates": true
  }'
```

### 2. Math Problem

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate the area of a circle with radius 5",
    "stream_updates": true
  }'
```

### 3. Factual Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who invented the telephone?",
    "stream_updates": true
  }'
```

### 4. Code/Logic Query

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the binary search algorithm",
    "stream_updates": true
  }'
```

### 5. Health Check

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

### 6. Pretty Print Response

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?"}' | python -m json.tool
```

## Python Examples

### Simple Python Client

```python
import requests
import json

def analyze_query(query: str):
    """Analyze a query using JUROR"""
    url = "http://localhost:8000/api/v1/analyze"
    payload = {"query": query, "stream_updates": True}
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    # Print verdict
    print(f"\nVERDICT: {result['verdict']}")
    print(f"Confidence: {result['verdict_confidence']}%")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\nOriginal Response:\n{result['draft_response']}")
    
    if result['corrected_response']:
        print(f"\nCorrected Response:\n{result['corrected_response']}")
    
    print(f"\nExecution Time: {result['execution_time']:.2f}s")
    print("\nAgent Timings:")
    for agent, time in result['agent_timings'].items():
        if time > 0:
            print(f"  {agent}: {time:.2f}s")

if __name__ == "__main__":
    analyze_query("What is the capital of France?")
```

### Async Client

```python
import asyncio
import aiohttp

async def analyze_async(query: str):
    """Async analysis"""
    url = "http://localhost:8000/api/v1/analyze"
    payload = {"query": query, "stream_updates": True}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            return result

if __name__ == "__main__":
    result = asyncio.run(analyze_async("Test query"))
    print(result['verdict'])
```

### WebSocket Client

```python
import asyncio
import websockets
import json

async def monitor_analysis():
    """Monitor analysis in real-time via WebSocket"""
    analysis_id = "550e8400-e29b-41d4-a716-446655440000"
    uri = f"ws://localhost:8000/api/v1/ws/jury/{analysis_id}"
    
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)
                print(f"[{event['event_type']}] {event.get('agent', '')}")
                
                if event['event_type'] == 'agent_completed':
                    print(f"  Score: {event.get('score')}")
                    print(f"  Status: {event.get('status')}")
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(monitor_analysis())
```

## JavaScript Examples

### Fetch API

```javascript
const analyzeQuery = async (query) => {
    const response = await fetch("http://localhost:8000/api/v1/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
            query: query,
            stream_updates: true 
        }),
    });
    
    const data = await response.json();
    
    console.log(`Verdict: ${data.verdict}`);
    console.log(`Confidence: ${data.verdict_confidence}%`);
    console.log(`Risk Level: ${data.risk_level}`);
    console.log(`Execution Time: ${data.execution_time.toFixed(2)}s`);
    
    return data;
};

// Usage
analyzeQuery("What is the capital of France?").then(result => {
    console.log(result);
});
```

### WebSocket Client

```javascript
const monitorAnalysis = (analysisId) => {
    const ws = new WebSocket(
        `ws://localhost:8000/api/v1/ws/jury/${analysisId}`
    );
    
    ws.onopen = () => {
        console.log("Connected to JUROR");
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`[${data.event_type}]`, data);
        
        // Update UI based on event
        switch(data.event_type) {
            case 'agent_started':
                updateAgentStatus(data.agent, 'active');
                break;
            case 'agent_completed':
                updateAgentStatus(data.agent, 'completed', data.score);
                break;
            case 'verdict_generated':
                showVerdict(data.verdict, data.confidence);
                break;
            case 'analysis_completed':
                console.log('Analysis complete!');
                ws.close();
                break;
        }
    };
    
    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
    
    return ws;
};

// Usage
const ws = monitorAnalysis("550e8400-e29b-41d4-a716-446655440000");
```

### Server-Sent Events

```javascript
const streamAnalysis = (query) => {
    const eventSource = new EventSource(
        `/api/v1/stream/analyze?query=${encodeURIComponent(query)}`
    );
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        
        if (data.event === 'complete') {
            console.log('Analysis complete!');
            eventSource.close();
        }
    };
    
    eventSource.onerror = () => {
        console.error('Stream error');
        eventSource.close();
    };
};

// Usage
streamAnalysis("What is AI?");
```

## Testing Scenarios

### Test 1: Should PASS

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who was the first president of the United States?"}'
```

**Expected:** PASS verdict, high confidence

### Test 2: Should FAIL (Hallucination)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "The Great Wall of China is in Japan"}'
```

**Expected:** FAIL verdict, corrected response

### Test 3: Math Heavy

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the derivative of x^3 + 2x?"}'
```

**Expected:** Math Validator runs, checks formula

### Test 4: Non-Factual

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me a story about an adventure"}'
```

**Expected:** Fact Checker skipped, Logic Auditor runs

## Batch Testing

### Test Multiple Queries

```bash
#!/bin/bash

queries=(
    "What is 2+2?"
    "Who invented electricity?"
    "The Earth orbits the Sun"
    "Calculate: sin(π/2)"
    "What is love?"
)

for query in "${queries[@]}"; do
    echo "Testing: $query"
    curl -X POST "http://localhost:8000/api/v1/analyze" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\"}" | python -m json.tool
    echo "---"
done
```

## Performance Testing

### Load Test

```bash
# Using Apache Bench
ab -n 100 -c 10 -p payload.json -T application/json http://localhost:8000/api/v1/analyze
```

### Sequential Testing

```python
import requests
import time

queries = [
    "What is AI?",
    "Calculate 2^10",
    "Who is Elon Musk?",
]

for query in queries:
    start = time.time()
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={"query": query}
    )
    elapsed = time.time() - start
    result = response.json()
    
    print(f"Query: {query}")
    print(f"Verdict: {result['verdict']}")
    print(f"Time: {elapsed:.2f}s")
    print()
```
