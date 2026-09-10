"""Machine state engine - determines current machine state from sensor data."""
from datetime import datetime, timedelta
from typing import Optional

from app.models.reading import MachineDataCollection, MachineReading
from app.models.context import MachineState


class MachineStateEngine:
    """Determines machine state from available sensor data."""
    
    def __init__(self, config: dict = None):
        """
        Initialize state engine.
        
        Args:
            config: State configuration with thresholds and rules
        """
        self.config = config or self._default_config()
        self.current_state = MachineState.UNKNOWN
        self.previous_state = MachineState.UNKNOWN
        self.state_timestamp = None
        self.state_history = []
    
    def _default_config(self) -> dict:
        """Default state detection configuration."""
        return {
            "states": {
                "running": {
                    "signals": ["MotorSpeed"],
                    "conditions": [{"MotorSpeed": {"min": 1000, "max": 2000}}]
                },
                "idle": {
                    "signals": ["MotorSpeed"],
                    "conditions": [{"MotorSpeed": {"min": 0, "max": 100}}]
                },
                "warning": {
                    "signals": ["MachineStatus"],
                    "conditions": [{"MachineStatus": {"equals": "WARNING"}}]
                },
                "stopped": {
                    "signals": ["MotorSpeed"],
                    "conditions": [{"MotorSpeed": {"equals": 0}}]
                }
            }
        }
    
    def determine_state(
        self,
        collection: MachineDataCollection
    ) -> tuple[str, Optional[str], float]:
        """
        Determine machine state from latest readings.
        
        Args:
            collection: MachineDataCollection with readings
            
        Returns:
            Tuple of (current_state, reason, confidence)
        """
        if not collection.readings:
            return MachineState.UNKNOWN, "No readings available", 0.0
        
        # Get latest readings by tag
        latest_readings = self._get_latest_readings(collection.readings)
        
        # Try to determine state from MachineStatus tag if available
        if "MachineStatus" in latest_readings:
            status_value = latest_readings["MachineStatus"].value
            if status_value in ["RUNNING", "IDLE", "WARNING", "STOPPED", "OFFLINE"]:
                return status_value, f"From MachineStatus tag: {status_value}", 0.95
        
        # Fallback: infer from MotorSpeed
        if "MotorSpeed" in latest_readings:
            speed = latest_readings["MotorSpeed"].value
            if isinstance(speed, (int, float)):
                if speed > 1000:
                    return MachineState.RUNNING, f"MotorSpeed {speed} RPM indicates running", 0.80
                elif speed > 0:
                    return MachineState.IDLE, f"MotorSpeed {speed} RPM indicates idle", 0.80
                elif speed == 0:
                    return MachineState.STOPPED, "MotorSpeed is zero", 0.80
        
        # No clear indicators
        return MachineState.UNKNOWN, "Cannot determine state from available data", 0.0
    
    def update_state(
        self,
        new_state: str,
        timestamp: datetime = None,
        reason: str = None
    ) -> None:
        """
        Update machine state.
        
        Args:
            new_state: New machine state
            timestamp: When state changed (default: now)
            reason: Reason for state change
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timestamp = timestamp
            self.state_history.append({
                "state": new_state,
                "timestamp": timestamp,
                "reason": reason
            })
    
    def get_state_duration(self, now: datetime = None) -> timedelta:
        """
        Get how long machine has been in current state.
        
        Args:
            now: Current time (default: utcnow)
            
        Returns:
            Duration timedelta
        """
        if now is None:
            now = datetime.utcnow()
        
        if self.state_timestamp is None:
            return timedelta(0)
        
        return now - self.state_timestamp
    
    def _get_latest_readings(self, readings: list[MachineReading]) -> dict[str, MachineReading]:
        """Get the most recent reading for each tag."""
        latest = {}
        for reading in readings:
            tag = reading.tag
            if tag not in latest or reading.timestamp > latest[tag].timestamp:
                latest[tag] = reading
        return latest
