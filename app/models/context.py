"""Machine context model."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class MachineState:
    """Machine operating states."""
    OFFLINE = "OFFLINE"
    STOPPED = "STOPPED"
    IDLE = "IDLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    WARNING = "WARNING"
    FAULT = "FAULT"
    MAINTENANCE = "MAINTENANCE"
    UNKNOWN = "UNKNOWN"


class MachineHealth:
    """Machine health status."""
    HEALTHY = "HEALTHY"
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class CommunicationStatus:
    """Communication status."""
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    LOST = "LOST"


class MachineContext(BaseModel):
    """Complete machine context - LLM-ready structured data."""
    
    timestamp: datetime = Field(..., description="Context generation timestamp")
    
    # Machine info
    machine_name: Optional[str] = Field(None, description="Machine/system name")
    machine_mode: Optional[str] = Field(None, description="Operating mode")
    machine_state: str = Field(default=MachineState.UNKNOWN, description="Current machine state")
    previous_state: Optional[str] = Field(None, description="Previous machine state")
    state_duration_seconds: int = Field(default=0, description="Seconds in current state")
    state_reason: Optional[str] = Field(None, description="Reason for current state")
    state_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in state determination")
    
    # Health
    health_status: str = Field(default=MachineHealth.UNKNOWN, description="Overall machine health")
    health_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Health score 0-100")
    health_reasons: list[str] = Field(default_factory=list, description="Reasons affecting health")
    
    # Current readings
    current_readings: dict[str, Any] = Field(default_factory=dict, description="Latest sensor values by tag")
    
    # Active alarms
    active_alarms: list[dict[str, Any]] = Field(default_factory=list, description="Currently active alarms")
    active_alarm_count: int = Field(default=0, description="Number of active alarms")
    
    # Recent events
    recent_events: list[dict[str, Any]] = Field(default_factory=list, description="Recent events (last N minutes)")
    recent_event_count: int = Field(default=0, description="Number of recent events")
    
    # Anomalies
    anomalies: list[dict[str, Any]] = Field(default_factory=list, description="Detected anomalies")
    anomaly_count: int = Field(default=0, description="Number of anomalies")
    
    # Trends
    trends: dict[str, str] = Field(default_factory=dict, description="Value trends by tag (INCREASING, DECREASING, STABLE, UNKNOWN)")
    
    # Statistics
    statistics: dict[str, dict[str, float]] = Field(default_factory=dict, description="Statistics per tag (min, max, mean, std)")
    
    # Communication
    communication_status: str = Field(default=CommunicationStatus.GOOD, description="System communication status")
    communication_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality 0-1")
    
    # Summary
    summary: str = Field(default="", description="Human-readable summary of machine state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-09-10T19:14:40.250828+00:00",
                "machine_name": "Boiler System",
                "machine_state": "RUNNING",
                "health_status": "WARNING",
                "health_score": 72.0,
                "current_readings": {
                    "Temperature": {"value": 24.7, "unit": "°C", "trend": "DECREASING"},
                    "Pressure": {"value": 1.032, "unit": "bar", "trend": "STABLE"}
                },
                "active_alarms": [],
                "summary": "Machine operating normally with temperature trending down"
            }
        }
