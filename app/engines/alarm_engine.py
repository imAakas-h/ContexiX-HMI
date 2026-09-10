"""Alarm and event engine - detects alarms and events from machine data."""
import uuid
from datetime import datetime
from typing import Optional

from app.models.reading import MachineReading, MachineDataCollection
from app.models.event import MachineEvent, Severity, EventStatus


class AlarmEngine:
    """Detects and manages machine alarms and events."""
    
    def __init__(self, config: dict = None):
        """
        Initialize alarm engine.
        
        Args:
            config: Alarm rules and thresholds
        """
        self.config = config or self._default_config()
        self.active_alarms: dict[str, MachineEvent] = {}
        self.recent_events: list[MachineEvent] = []
        self.alarm_history: list[MachineEvent] = []  # Track all alarms including cleared
        self._event_counter = 0
        self._last_alarm_state = {}  # Track state to avoid duplicate alarms
    
    def _default_config(self) -> dict:
        """Default alarm configuration from YOUR data."""
        return {
            "thresholds": {
                "Temperature": {"high": 25.0, "low": 15.0},
                "Pressure": {"high": 1.3, "low": 0.8},
                "MotorSpeed": {"high": 1600.0, "low": 1400.0},
                "MotorCurrent": {"high": 6.0, "low": 4.5},
                "Vibration": {"high": 0.8, "low": 0.4}
            }
        }
    
    def check_readings(
        self,
        collection: MachineDataCollection
    ) -> list[MachineEvent]:
        """
        Check ALL readings for alarm conditions (chronological).
        
        Args:
            collection: MachineDataCollection to check
            
        Returns:
            List of all events detected in chronological order
        """
        all_events = []
        
        # Process ALL readings in chronological order
        for reading in collection.readings:
            events = self.check_reading(reading)
            all_events.extend(events)
        
        return all_events
    
    def check_reading(self, reading: MachineReading) -> list[MachineEvent]:
        """
        Check a single reading for alarm conditions.
        
        Args:
            reading: MachineReading to check
            
        Returns:
            List of events (empty if no alarms)
        """
        events = []
        tag = reading.tag
        thresholds = self.config.get("thresholds", {}).get(tag)
        
        if not thresholds or not isinstance(reading.value, (int, float)):
            return events
        
        # Create state key
        state_key = f"{tag}_{reading.node_id}"
        
        # Check high threshold
        if "high" in thresholds and reading.value > thresholds["high"]:
            # Only create alarm if we weren't already in high state
            if state_key not in self._last_alarm_state or self._last_alarm_state[state_key] != "HIGH":
                event = self._create_alarm(
                    reading=reading,
                    event_type=f"{tag.upper()}_HIGH",
                    threshold=thresholds["high"],
                    severity=Severity.WARNING,
                    direction="exceeded"
                )
                events.append(event)
                self.alarm_history.append(event)
                self._record_alarm(event)
                self._last_alarm_state[state_key] = "HIGH"
        
        # Check low threshold
        elif "low" in thresholds and reading.value < thresholds["low"]:
            # Only create alarm if we weren't already in low state
            if state_key not in self._last_alarm_state or self._last_alarm_state[state_key] != "LOW":
                event = self._create_alarm(
                    reading=reading,
                    event_type=f"{tag.upper()}_LOW",
                    threshold=thresholds["low"],
                    severity=Severity.WARNING,
                    direction="fallen below"
                )
                events.append(event)
                self.alarm_history.append(event)
                self._record_alarm(event)
                self._last_alarm_state[state_key] = "LOW"
        
        else:
            # Value is normal - clear alarm state
            if state_key in self._last_alarm_state:
                del self._last_alarm_state[state_key]
        
        return events
    
    def _create_alarm(
        self,
        reading: MachineReading,
        event_type: str,
        threshold: float,
        severity: Severity,
        direction: str = "crossed"
    ) -> MachineEvent:
        """Create a MachineEvent from a reading."""
        alarm_id = f"evt_{reading.node_id.replace(';', '_').replace('=', '_')}_{self._event_counter}"
        self._event_counter += 1
        
        message = f"{reading.tag} {direction} threshold ({threshold})"
        
        return MachineEvent(
            event_id=alarm_id,
            timestamp=reading.timestamp,
            type=event_type,
            severity=severity,
            node_id=reading.node_id,
            tag=reading.tag,
            value=reading.value,
            threshold=threshold,
            message=message,
            status=EventStatus.ACTIVE
        )
    
    def _record_alarm(self, event: MachineEvent) -> None:
        """Record an alarm in tracking."""
        alarm_key = f"{event.node_id}_{event.type}"
        
        # Keep the latest version of this alarm
        self.active_alarms[alarm_key] = event
        self.recent_events.append(event)
    
    def clear_alarm(self, alarm_id: str, timestamp: datetime = None) -> Optional[MachineEvent]:
        """
        Clear an active alarm.
        
        Args:
            alarm_id: Event ID to clear
            timestamp: When alarm was cleared
            
        Returns:
            Cleared MachineEvent or None
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        for key, event in list(self.active_alarms.items()):
            if event.event_id == alarm_id:
                event.status = EventStatus.CLEARED
                event.cleared_at = timestamp
                del self.active_alarms[key]
                return event
        
        return None
    
    def get_active_alarms(self) -> list[MachineEvent]:
        """Get all currently active alarms."""
        return list(self.active_alarms.values())
    
    def get_alarm_history(self) -> list[MachineEvent]:
        """Get complete alarm history."""
        return self.alarm_history
    
    def get_recent_events(self, limit: int = 10) -> list[MachineEvent]:
        """Get recent events."""
        return self.recent_events[-limit:]

