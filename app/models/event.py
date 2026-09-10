"""Event and alarm models."""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of machine events."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Severity(str, Enum):
    """Event severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class EventStatus(str, Enum):
    """Event status."""
    ACTIVE = "ACTIVE"
    CLEARED = "CLEARED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class MachineEvent(BaseModel):
    """A machine event or alarm."""
    
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="When the event occurred")
    type: str = Field(..., description="Event type (TEMPERATURE_HIGH, PRESSURE_LOW, etc.)")
    severity: Severity = Field(default=Severity.INFO, description="Event severity")
    component: Optional[str] = Field(None, description="Affected component (e.g., 'Boiler', 'Motor')")
    node_id: Optional[str] = Field(None, description="Associated node ID")
    tag: Optional[str] = Field(None, description="Associated tag name")
    value: Optional[float] = Field(None, description="Value that triggered the event")
    threshold: Optional[float] = Field(None, description="Threshold that was exceeded")
    message: str = Field(..., description="Human-readable event description")
    status: EventStatus = Field(default=EventStatus.ACTIVE, description="Event status")
    cleared_at: Optional[datetime] = Field(None, description="When event was cleared")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_20260910_001",
                "timestamp": "2026-09-10T19:09:39.314740+00:00",
                "type": "TEMPERATURE_HIGH",
                "severity": "WARNING",
                "component": "Boiler",
                "node_id": "ns=2;i=2",
                "tag": "Temperature",
                "value": 92.0,
                "threshold": 85.0,
                "message": "Boiler temperature exceeded normal range",
                "status": "ACTIVE"
            }
        }
