"""
FastAPI routes for JUROR analysis endpoints.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import AsyncGenerator

from app.models.agent_models import AnalysisRequest, AnalysisResponse
from app.orchestration.pipeline import JurorPipeline
from app.websocket.manager import connection_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["jury"])

# Store active analyses
active_analyses = {}


async def event_callback(event: dict):
    """Callback for pipeline events."""
    # Can be used to store or broadcast events
    logger.debug(f"Pipeline event: {event.get('event_type')}")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze a query through the JUROR pipeline.
    
    Args:
        request: Analysis request with query
        
    Returns:
        Complete analysis response
    """
    logger.info(f"Analyze endpoint called with query: {request.query[:100]}")
    
    try:
        pipeline = JurorPipeline(event_callback=event_callback)
        response = await pipeline.run(request.query)
        
        # Store analysis
        active_analyses[response.analysis_id] = response
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "JUROR Backend",
        "version": "1.0.0"
    }


@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve stored analysis."""
    if analysis_id in active_analyses:
        return active_analyses[analysis_id]
    raise HTTPException(status_code=404, detail="Analysis not found")


@router.websocket("/ws/jury/{analysis_id}")
async def websocket_jury_endpoint(websocket: WebSocket, analysis_id: str):
    """
    WebSocket endpoint for real-time jury updates.
    
    Args:
        websocket: WebSocket connection
        analysis_id: Analysis ID to subscribe to
    """
    await connection_manager.connect(websocket)
    await connection_manager.subscribe_to_analysis(analysis_id, websocket)
    
    try:
        # Send initial subscription confirmation
        await websocket.send_json({
            "event_type": "subscribed",
            "analysis_id": analysis_id
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client messages if needed
            if message.get("type") == "ping":
                await connection_manager.send_personal(websocket, {"type": "pong"})
    
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
        await connection_manager.unsubscribe_from_analysis(analysis_id, websocket)
        logger.info(f"WebSocket disconnected from analysis {analysis_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await connection_manager.disconnect(websocket)


@router.get("/stream/analyze")
async def stream_analyze(query: str) -> StreamingResponse:
    """
    Stream analysis progress as Server-Sent Events.
    
    Args:
        query: Query to analyze
        
    Returns:
        SSE stream
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for analysis progress."""
        try:
            pipeline = JurorPipeline()
            
            # Emit initial event
            yield f"data: {json.dumps({'event': 'start', 'query': query})}\n\n"
            
            # Run pipeline
            response = await pipeline.run(query)
            
            # Emit final event
            yield f"data: {json.dumps({'event': 'complete', 'analysis_id': response.analysis_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
