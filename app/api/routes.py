"""FastAPI routes for Machine Context Engine."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from jinja2 import Template

from app.main import MachineContextEngine
from app.inputs.mock_fleet import BOILER_NAMES, generate_fleet
from app.context.operator_query import resolve_query
from app.context.suggest_engine import SuggestEngine
from app.ui.nlp_templates import NLP_NARRATIVE_TEMPLATE


class EngineStatus(BaseModel):
    """Engine status response."""
    initialized: bool
    node_count: int
    last_context_timestamp: Optional[str] = None
    unknown_nodes_count: int


class ProcessRequest(BaseModel):
    """Request to process machine data."""
    machine_data_file: str


class QueryRequest(BaseModel):
    """Natural-language operator request."""
    text: str
    machine: str = "Boiler-01"


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

    fleet_collections = generate_fleet()
    fleet_contexts = {
        name: engine.process_collection(collection, name)
        for name, collection in fleet_collections.items()
    }
    web_root = Path(__file__).resolve().parents[2] / "web"
    suggest_engine = SuggestEngine()

    def series_for(machine: str) -> dict[str, list[dict]]:
        """Serialize the selected unit's actual rolling samples for graphing."""
        grouped: dict[str, list[dict]] = {}
        for reading in fleet_collections[machine].readings:
            grouped.setdefault(reading.tag, []).append({
                "timestamp": reading.timestamp.isoformat(),
                "value": reading.value,
                "unit": reading.unit or "",
            })
        return grouped

    app.mount("/assets", StaticFiles(directory=web_root / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def dashboard():
        return FileResponse(web_root / "index.html")

    @app.get("/api/fleet")
    async def get_fleet():
        return {
            "units": [
                {
                    **fleet_contexts[name].model_dump(mode="json"),
                    "series": series_for(name),
                }
                for name in BOILER_NAMES
            ],
            "names": list(BOILER_NAMES),
        }

    @app.get("/api/fleet/{machine}")
    async def get_fleet_machine(machine: str):
        context = fleet_contexts.get(machine)
        if not context:
            raise HTTPException(status_code=404, detail="Unknown boiler unit")
        return {**context.model_dump(mode="json"), "series": series_for(machine)}

    @app.post("/api/query")
    async def operator_query(request: QueryRequest):
        resolved = resolve_query(request.text, request.machine)
        if resolved.machine == "ALL":
            response = "\n".join(
                f"{name}: {context.machine_state}, health {context.health_score:.0f}/100, "
                f"{context.active_alarm_count} active alarm(s)"
                for name, context in fleet_contexts.items()
            )
            return {"query": resolved.__dict__, "response": response}

        context = fleet_contexts.get(resolved.machine)
        if not context:
            raise HTTPException(status_code=404, detail="Unknown boiler unit")
        report_data = context.model_dump(mode="json")
        if resolved.intent == "comprehensive":
            response = Template(NLP_NARRATIVE_TEMPLATE).render(
                **report_data, generated_at=context.timestamp.isoformat()
            )
        elif resolved.intent == "alarms":
            response = f"{context.machine_name} has {context.active_alarm_count} active alarm(s). " \
                + ("; ".join(a["message"] for a in context.active_alarms) or "No threshold violations are active.")
        elif resolved.intent == "health":
            response = f"{context.machine_name} is {context.health_status.lower()} at {context.health_score:.0f}/100. " \
                + (" ".join(context.health_reasons) or "All monitored health factors are nominal.")
        else:
            metric_aliases = {
                "temperature": "Temperature", "temp": "Temperature", "heat": "Temperature",
                "pressure": "Pressure", "bar": "Pressure", "motor current": "MotorCurrent",
                "current": "MotorCurrent", "amps": "MotorCurrent", "motor speed": "MotorSpeed",
                "speed": "MotorSpeed", "rpm": "MotorSpeed", "vibration": "Vibration",
                "machine status": "MachineStatus", "status": "MachineStatus", "state": "MachineStatus",
            }
            normalized_text = request.text.lower()
            metric = next(
                (tag for alias, tag in metric_aliases.items() if alias in normalized_text),
                None,
            )
            if metric and metric in context.current_readings:
                reading = context.current_readings[metric]
                stats = context.statistics.get(metric, {})
                response = (
                    f"{context.machine_name} {metric}: {reading['value']} {reading.get('unit', '')}. "
                    f"Trend: {reading.get('trend', 'UNKNOWN')}. "
                    f"Observed range: {stats.get('min', 'n/a')} to {stats.get('max', 'n/a')}."
                )
            else:
                response = f"{context.machine_name} status: {context.machine_state}."
        return {"query": resolved.__dict__, "response": response, "context": report_data}

    @app.get("/api/suggest")
    async def suggest(query: str = ""):
        """Return ranked autocomplete options for live operator search."""
        return [
            {"text": item.text, "category": item.category, "icon": item.icon, "display": item.display}
            for item in suggest_engine.suggest(query)
        ]
    
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
