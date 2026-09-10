"""Context builder - orchestrates all engines to build machine context."""
from datetime import datetime
from typing import Optional

from app.models.context import MachineContext, MachineHealth
from app.models.reading import MachineDataCollection
from app.models.node import NodeMetadataRegistry
from app.engines.machine_state import MachineStateEngine
from app.engines.alarm_engine import AlarmEngine
from app.engines.trend_engine import TrendEngine
from app.engines.anomaly_engine import AnomalyEngine
from app.engines.health_engine import HealthEngine


class ContextBuilder:
    """Builds complete machine context from normalized data."""
    
    def __init__(
        self,
        node_registry: NodeMetadataRegistry,
        state_engine: MachineStateEngine = None,
        alarm_engine: AlarmEngine = None,
        trend_engine: TrendEngine = None,
        anomaly_engine: AnomalyEngine = None,
        health_engine: HealthEngine = None
    ):
        """
        Initialize context builder with engines.
        
        Args:
            node_registry: NodeMetadataRegistry with all node definitions
            state_engine: MachineStateEngine (created if None)
            alarm_engine: AlarmEngine (created if None)
            trend_engine: TrendEngine (created if None)
            anomaly_engine: AnomalyEngine (created if None)
            health_engine: HealthEngine (created if None)
        """
        self.node_registry = node_registry
        self.state_engine = state_engine or MachineStateEngine()
        self.alarm_engine = alarm_engine or AlarmEngine()
        self.trend_engine = trend_engine or TrendEngine()
        self.anomaly_engine = anomaly_engine or AnomalyEngine()
        self.health_engine = health_engine or HealthEngine()
        self.last_context = None
    
    def build(self, collection: MachineDataCollection) -> MachineContext:
        """
        Build complete machine context from collection.
        
        Args:
            collection: MachineDataCollection with normalized readings
            
        Returns:
            Complete MachineContext
        """
        timestamp = datetime.utcnow()
        
        # Step 1: Determine machine state
        current_state, state_reason, state_confidence = self.state_engine.determine_state(collection)
        
        # Step 2: Get latest readings
        latest_readings = self._get_latest_readings(collection)
        
        # Step 3: Calculate trends
        trends = self.trend_engine.calculate_trends(collection)
        
        # Step 4: Check for alarms - process ALL readings chronologically
        all_alarm_events = self.alarm_engine.check_readings(collection)
        active_alarms = self.alarm_engine.get_active_alarms()
        recent_events = all_alarm_events[-20:]  # Last 20 alarm events
        
        # Step 5: Detect anomalies
        anomalies = self.anomaly_engine.detect_anomalies(collection)
        
        # Step 6: Calculate statistics
        statistics = self._calculate_statistics(collection)
        
        # Step 7: Determine communication quality
        communication_quality = self._assess_communication_quality(collection)
        
        # Step 8: Calculate health
        health_status, health_score, health_reasons = self.health_engine.calculate_health(
            active_alarms=active_alarms,
            anomalies=anomalies,
            communication_quality=communication_quality,
            machine_state=current_state
        )
        
        # Step 9: Build context
        context = MachineContext(
            timestamp=timestamp,
            machine_name="Machine System",  # Can be set from config
            machine_state=current_state,
            previous_state=self.state_engine.previous_state,
            state_duration_seconds=int(self.state_engine.get_state_duration().total_seconds()),
            state_reason=state_reason,
            state_confidence=state_confidence,
            health_status=health_status,
            health_score=health_score,
            health_reasons=health_reasons,
            current_readings=self._format_readings(latest_readings, trends),
            active_alarms=[self._format_alarm(a) for a in active_alarms],
            active_alarm_count=len(active_alarms),
            recent_events=[self._format_event(e) for e in recent_events],
            recent_event_count=len(recent_events),
            anomalies=anomalies,
            anomaly_count=len(anomalies),
            trends={tag: info["trend"] for tag, info in trends.items()},
            statistics=statistics,
            communication_status="GOOD" if communication_quality > 0.8 else "DEGRADED",
            communication_quality=communication_quality,
            summary=self._build_summary(current_state, health_status, active_alarms, anomalies)
        )
        
        self.last_context = context
        return context
    
    def _get_latest_readings(self, collection: MachineDataCollection) -> dict:
        """Get the most recent reading for each tag."""
        latest = {}
        for reading in collection.readings:
            tag = reading.tag
            if tag not in latest or reading.timestamp > latest[tag]["timestamp"]:
                latest[tag] = {
                    "timestamp": reading.timestamp,
                    "node_id": reading.node_id,
                    "value": reading.value,
                    "data_type": reading.data_type,
                    "quality": reading.quality,
                    "unit": reading.unit
                }
        return latest
    
    def _format_readings(self, latest_readings: dict, trends: dict) -> dict:
        """Format readings with trends."""
        formatted = {}
        for tag, reading_data in latest_readings.items():
            trend_info = trends.get(tag, {})
            formatted[tag] = {
                "value": reading_data["value"],
                "unit": reading_data["unit"],
                "trend": trend_info.get("trend", "UNKNOWN"),
                "quality": reading_data["quality"]
            }
        return formatted
    
    def _calculate_statistics(self, collection: MachineDataCollection) -> dict:
        """Calculate statistics for all numeric readings."""
        stats = {}
        readings_by_tag = {}
        
        for reading in collection.readings:
            if reading.tag not in readings_by_tag:
                readings_by_tag[reading.tag] = []
            readings_by_tag[reading.tag].append(reading)
        
        for tag, readings in readings_by_tag.items():
            numeric_values = [r.value for r in readings if isinstance(r.value, (int, float))]
            if numeric_values:
                stats[tag] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": sum(numeric_values) / len(numeric_values),
                    "count": len(numeric_values)
                }
        
        return stats
    
    def _assess_communication_quality(self, collection: MachineDataCollection) -> float:
        """Assess data quality from StatusCode values."""
        if not collection.readings:
            return 0.0
        
        good_quality = sum(1 for r in collection.readings if r.quality == "GOOD")
        total = len(collection.readings)
        
        return good_quality / total if total > 0 else 0.0
    
    def _format_alarm(self, alarm) -> dict:
        """Format alarm for context."""
        return {
            "event_id": alarm.event_id,
            "timestamp": alarm.timestamp.isoformat(),
            "type": alarm.type,
            "severity": alarm.severity,
            "tag": alarm.tag,
            "value": alarm.value,
            "threshold": alarm.threshold,
            "message": alarm.message
        }
    
    def _format_event(self, event) -> dict:
        """Format event for context."""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "type": event.type,
            "severity": event.severity,
            "message": event.message,
            "status": event.status
        }
    
    def _build_summary(
        self,
        state: str,
        health: str,
        alarms: list,
        anomalies: list
    ) -> str:
        """Build human-readable summary."""
        parts = []
        
        parts.append(f"Machine is {state.lower()}")
        parts.append(f"Health: {health}")
        
        if alarms:
            parts.append(f"{len(alarms)} active alarm(s)")
        
        if anomalies:
            parts.append(f"{len(anomalies)} anomaly/ies")
        
        return " | ".join(parts)
