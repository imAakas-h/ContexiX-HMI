"""Machine reading and telemetry models."""
from datetime import datetime
from typing import Any, Optional, Union
from pydantic import BaseModel, Field


class QualityStatus:
    """OPC UA quality status levels."""
    GOOD = "GOOD"
    UNCERTAIN = "UNCERTAIN"
    BAD = "BAD"
    UNKNOWN = "UNKNOWN"


class MachineReading(BaseModel):
    """A single machine sensor reading."""
    
    timestamp: datetime = Field(..., description="When the reading was taken")
    node_id: str = Field(..., description="OPC UA node ID (e.g., 'ns=2;i=2')")
    tag: str = Field(..., description="Tag name (e.g., 'Temperature')")
    value: Union[float, str, bool, int] = Field(..., description="The sensor value")
    data_type: str = Field(default="Unknown", description="Data type of the value")
    quality: str = Field(default=QualityStatus.UNKNOWN, description="Quality status (GOOD, UNCERTAIN, BAD, UNKNOWN)")
    unit: Optional[str] = Field(None, description="Engineering unit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-09-10T19:09:37.293204+00:00",
                "node_id": "ns=2;i=2",
                "tag": "Temperature",
                "value": 22.39,
                "data_type": "float",
                "quality": "GOOD",
                "unit": "°C"
            }
        }


class MachineDataCollection(BaseModel):
    """A collection of machine readings with metadata."""
    
    source: str = Field(..., description="Data source (e.g., OPC UA server URL)")
    duration_seconds: int = Field(..., description="Duration of collection period")
    sampling_interval_seconds: int = Field(..., description="Sampling interval in seconds")
    start_time: datetime = Field(..., description="Collection start time")
    end_time: datetime = Field(..., description="Collection end time")
    readings: list[MachineReading] = Field(default_factory=list, description="List of sensor readings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "opc.tcp://localhost:4840/mce/server/",
                "duration_seconds": 300,
                "sampling_interval_seconds": 1,
                "start_time": "2026-09-10T19:09:37.292205+00:00",
                "end_time": "2026-09-10T19:14:40.250828+00:00",
                "readings": []
            }
        }
