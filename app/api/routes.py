"""FastAPI routes for Machine Context Engine."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import json
import tempfile
from pathlib import Path

from app.main import MachineContextEngine


class EngineStatus(BaseModel):
    """Engine status response."""
    initialized: bool
    node_count: int
    last_context_timestamp: Optional[str] = None
    unknown_nodes_count: int


class ProcessRequest(BaseModel):
    """Request to process machine data."""
    machine_data_file: str


def create_app(engine: MachineContextEngine) -> FastAPI:
    """
    Create FastAPI application with routes.
    
    Args:
        engine: MachineContextEngine instance
        
    Returns:
        FastAPI app
    """
    app = FastAPI(
        title="Machine Context Engine",
        description="REST API for machine context analysis",
        version="1.0.0"
    )
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/engine/status", response_model=EngineStatus)
    async def engine_status():
        """Get engine status."""
        return {
            "initialized": True,
            "node_count": len(engine.get_node_registry().list_nodes()),
            "last_context_timestamp": engine.last_context.timestamp.isoformat() if engine.last_context else None,
            "unknown_nodes_count": len(engine.get_unknown_nodes())
        }
    
    @app.post("/process")
    async def process_data(request: ProcessRequest):
        """Process machine data file."""
        try:
            context = engine.process(request.machine_data_file)
            return context.model_dump(mode='json')
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"File not found: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/context")
    async def get_context():
        """Get last generated context."""
        if engine.last_context:
            return engine.last_context.model_dump(mode='json')
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/context/llm")
    async def get_llm_context():
        """Get LLM-ready context string."""
        llm_context = engine.get_llm_context()
        if llm_context:
            return {"llm_context": llm_context}
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/context/compact")
    async def get_compact_context():
        """Get compact context string."""
        compact = engine.get_compact_context()
        if compact:
            return {"compact_context": compact}
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/machine")
    async def get_machine():
        """Get current machine info."""
        if engine.last_context:
            return {
                "name": engine.last_context.machine_name,
                "state": engine.last_context.machine_state,
                "health": engine.last_context.health_status,
                "health_score": engine.last_context.health_score
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/machine/state")
    async def get_machine_state():
        """Get machine state."""
        if engine.last_context:
            return {
                "state": engine.last_context.machine_state,
                "previous_state": engine.last_context.previous_state,
                "duration_seconds": engine.last_context.state_duration_seconds,
                "reason": engine.last_context.state_reason,
                "confidence": engine.last_context.state_confidence
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/machine/health")
    async def get_machine_health():
        """Get machine health."""
        if engine.last_context:
            return {
                "status": engine.last_context.health_status,
                "score": engine.last_context.health_score,
                "reasons": engine.last_context.health_reasons
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/alarms")
    async def get_alarms():
        """Get active alarms."""
        if engine.last_context:
            return {
                "count": engine.last_context.active_alarm_count,
                "alarms": engine.last_context.active_alarms
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/events")
    async def get_events():
        """Get recent events."""
        if engine.last_context:
            return {
                "count": engine.last_context.recent_event_count,
                "events": engine.last_context.recent_events
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/anomalies")
    async def get_anomalies():
        """Get detected anomalies."""
        if engine.last_context:
            return {
                "count": engine.last_context.anomaly_count,
                "anomalies": engine.last_context.anomalies
            }
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/nodes")
    async def get_nodes():
        """Get all registered nodes."""
        nodes = engine.get_node_registry().list_nodes()
        return {
            "total": len(nodes),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "tag": n.tag,
                    "data_type": n.data_type,
                    "unit": n.unit
                }
                for n in nodes
            ]
        }
    
    @app.get("/readings")
    async def get_readings():
        """Get current readings."""
        if engine.last_context:
            return engine.last_context.current_readings
        raise HTTPException(status_code=404, detail="No context available")
    
    @app.get("/trends")
    async def get_trends():
        """Get current trends."""
        if engine.last_context:
            return engine.last_context.trends
        raise HTTPException(status_code=404, detail="No context available")
    
    return app
