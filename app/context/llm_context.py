"""LLM context generator - creates concise, LLM-ready machine context."""
from app.models.context import MachineContext


class LLMContextGenerator:
    """Generates concise, structured text context for LLM consumption."""
    
    def generate(self, context: MachineContext) -> str:
        """
        Generate LLM-ready context string.
        
        Args:
            context: MachineContext
            
        Returns:
            Formatted context string for LLM
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(f"MACHINE CONTEXT - {context.timestamp.isoformat()}")
        lines.append("=" * 60)
        lines.append("")
        
        # Machine info
        lines.append(f"MACHINE: {context.machine_name}")
        lines.append(f"STATE: {context.machine_state}")
        if context.state_reason:
            lines.append(f"  Reason: {context.state_reason}")
            lines.append(f"  Confidence: {context.state_confidence:.0%}")
        lines.append(f"  Duration in state: {context.state_duration_seconds}s")
        lines.append("")
        
        # Health
        lines.append(f"HEALTH: {context.health_status}")
        lines.append(f"  Score: {context.health_score:.0f}/100")
        if context.health_reasons:
            lines.append("  Factors:")
            for reason in context.health_reasons:
                lines.append(f"    - {reason}")
        lines.append("")
        
        # Current readings
        lines.append("CURRENT CONDITIONS:")
        if context.current_readings:
            for tag, reading in context.current_readings.items():
                value = reading.get("value")
                unit = reading.get("unit", "")
                trend = reading.get("trend", "")
                line = f"  {tag}: {value} {unit}"
                if trend and trend != "UNKNOWN":
                    line += f" ({trend})"
                lines.append(line)
        else:
            lines.append("  No readings available")
        lines.append("")
        
        # Active alarms
        lines.append(f"ACTIVE ALARMS: {context.active_alarm_count}")
        if context.active_alarms:
            for alarm in context.active_alarms[:5]:  # Limit to 5
                severity = alarm.get("severity", "")
                tag = alarm.get("tag", "")
                message = alarm.get("message", "")
                lines.append(f"  [{severity}] {tag}: {message}")
            if len(context.active_alarms) > 5:
                lines.append(f"  ... and {len(context.active_alarms) - 5} more")
        else:
            lines.append("  None")
        lines.append("")
        
        # Recent events
        lines.append(f"RECENT EVENTS: {context.recent_event_count}")
        if context.recent_events:
            for event in context.recent_events[:3]:  # Limit to 3
                event_type = event.get("type", "")
                message = event.get("message", "")
                lines.append(f"  {event_type}: {message}")
            if len(context.recent_events) > 3:
                lines.append(f"  ... and {len(context.recent_events) - 3} more")
        else:
            lines.append("  None")
        lines.append("")
        
        # Anomalies
        lines.append(f"ANOMALIES: {context.anomaly_count}")
        if context.anomalies:
            for anomaly in context.anomalies[:3]:  # Limit to 3
                tag = anomaly.get("tag", "")
                anom_type = anomaly.get("type", "")
                message = anomaly.get("message", "")
                lines.append(f"  {tag} ({anom_type}): {message}")
            if len(context.anomalies) > 3:
                lines.append(f"  ... and {len(context.anomalies) - 3} more")
        else:
            lines.append("  None")
        lines.append("")
        
        # Trends
        if context.trends:
            lines.append("TRENDS:")
            for tag, trend in context.trends.items():
                if trend != "UNKNOWN":
                    lines.append(f"  {tag}: {trend}")
        lines.append("")
        
        # Communication
        lines.append(f"COMMUNICATION: {context.communication_status}")
        lines.append(f"  Data quality: {context.communication_quality:.0%}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(f"  {context.summary}")
        lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_compact(self, context: MachineContext) -> str:
        """
        Generate compact single-line context.
        
        Args:
            context: MachineContext
            
        Returns:
            Single-line summary
        """
        parts = []
        
        parts.append(f"{context.machine_name}:")
        parts.append(f"State={context.machine_state}")
        parts.append(f"Health={context.health_status}({context.health_score:.0f})")
        
        if context.active_alarm_count > 0:
            parts.append(f"Alarms={context.active_alarm_count}")
        
        if context.anomaly_count > 0:
            parts.append(f"Anomalies={context.anomaly_count}")
        
        if context.current_readings:
            readings = [
                f"{tag}={r.get('value')}" 
                for tag, r in list(context.current_readings.items())[:3]
            ]
            parts.append("Values=[" + ",".join(readings) + "]")
        
        return " | ".join(parts)
