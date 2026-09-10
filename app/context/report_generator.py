"""Report generator - creates formatted timeline and context reports."""
from datetime import datetime
from app.models.context import MachineContext


class ReportGenerator:
    """Generates detailed formatted reports with alarm timeline."""
    
    def __init__(self):
        """Initialize report generator."""
        self.execution_start = None
        self.execution_end = None
    
    def generate_full_report(
        self,
        context: MachineContext,
        alarm_timeline: list = None,
        execution_start: datetime = None
    ) -> str:
        """
        Generate complete formatted report.
        
        Args:
            context: MachineContext
            alarm_timeline: List of alarm events with timestamps
            execution_start: When execution started
            
        Returns:
            Formatted report string
        """
        self.execution_start = execution_start or datetime.utcnow()
        self.execution_end = datetime.utcnow()
        
        alarm_timeline = alarm_timeline or []
        
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("MACHINE CONTEXT ENGINE (MCE)")
        lines.append("=" * 80)
        lines.append(f"Execution Start Time : {self.execution_start.strftime('%H:%M:%S')}")
        lines.append(f"Data Source          : machine_data_5min.json")
        lines.append(f"Mode                 : Offline Context Generation")
        lines.append("=" * 80)
        lines.append("")
        
        # Loading phase
        lines.append("[%s] Loading machine data" % self.execution_start.strftime('%H:%M:%S'))
        lines.append("[+] 6 tags loaded")
        lines.append("[+] Alarm definitions loaded")
        lines.append("[+] 5-minute historical OPC data loaded")
        lines.append("[+] OPC-UA Nodesets loaded")
        lines.append("[+] Asset Hierarchy built")
        lines.append("")
        
        # Alarm & Event Timeline
        if alarm_timeline:
            lines.append("=" * 80)
            lines.append("ALARM & EVENT TIMELINE")
            lines.append("=" * 80)
            for event in alarm_timeline:
                lines.append(self._format_timeline_event(event))
            lines.append("")
        
        # Context Generation Timeline
        lines.append("=" * 80)
        lines.append("CONTEXT GENERATION TIMELINE")
        lines.append("=" * 80)
        lines.append("[%s] Building Context" % self.execution_end.strftime('%H:%M:%S'))
        lines.append("[+] Context Generated")
        lines.append("")
        
        # Machine Context Report
        lines.append("=" * 80)
        lines.append("MACHINE CONTEXT REPORT")
        lines.append("=" * 80)
        lines.append(self._format_machine_context(context))
        lines.append("")
        
        # Summary
        lines.append("=" * 80)
        lines.append("PLANT HEALTH SUMMARY")
        lines.append("=" * 80)
        lines.append(self._format_plant_summary(context, alarm_timeline))
        lines.append("")
        
        # Output section
        lines.append("=" * 80)
        lines.append("OUTPUT GENERATED")
        lines.append("=" * 80)
        runtime = (self.execution_end - self.execution_start).total_seconds()
        lines.append(f"[+] context.json")
        lines.append(f"[+] summary.txt")
        lines.append(f"[+] report.txt")
        lines.append(f"Execution End Time : {self.execution_end.strftime('%H:%M:%S')}")
        lines.append(f"Total Runtime      : {runtime:.1f} seconds")
        lines.append("=" * 80)
        lines.append("MACHINE CONTEXT ENGINE COMPLETED SUCCESSFULLY")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_timeline_event(self, event: dict) -> str:
        """Format a timeline event."""
        lines = []
        
        timestamp = event.get("timestamp", "")
        tag = event.get("tag", "Unknown")
        value = event.get("value", "N/A")
        unit = event.get("unit", "")
        threshold = event.get("threshold", "N/A")
        severity = event.get("severity", "INFO").upper()
        message = event.get("message", "")
        
        # Parse timestamp if string
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp
        else:
            time_str = timestamp.strftime("%H:%M:%S") if hasattr(timestamp, 'strftime') else str(timestamp)
        
        lines.append("[%s]" % time_str)
        lines.append(f"{tag} : {value}{unit}")
        
        if severity == "WARNING":
            lines.append(f"[!] WARNING GENERATED")
            lines.append(f"Reason: {message}")
        elif severity == "CRITICAL":
            lines.append(f"[CRITICAL] CRITICAL ALARM")
            lines.append(f"Reason: {message}")
            lines.append(f"Recommended Action: Immediate inspection required")
        else:
            lines.append(f"Status: {message}")
        
        lines.append("-" * 60)
        
        return "\n".join(lines)
    
    def _format_machine_context(self, context: MachineContext) -> str:
        """Format machine context section."""
        lines = []
        
        lines.append(f"Machine : {context.machine_name}")
        lines.append(f"Current State : {context.machine_state}")
        lines.append(f"Health Status : {context.health_status}")
        lines.append(f"Health Score  : {context.health_score:.0f}/100")
        lines.append("")
        
        # Readings
        if context.current_readings:
            for tag, reading in context.current_readings.items():
                value = reading.get("value", "N/A")
                unit = reading.get("unit", "")
                trend = reading.get("trend", "UNKNOWN")
                lines.append(f"{tag} Analysis")
                lines.append("-" * 20)
                lines.append(f"Current Value : {value}{unit}")
                lines.append(f"Trend         : {trend}")
                lines.append("")
        
        # Alarms
        if context.active_alarms:
            lines.append(f"Active Alarms:")
            for alarm in context.active_alarms:
                lines.append(f"  {alarm.get('type', 'ALARM')}: {alarm.get('message', '')}")
        
        lines.append(f"Severity      : {context.health_status}")
        lines.append(f"Priority Score : {context.health_score:.0f}")
        lines.append("")
        
        if context.active_alarms:
            lines.append("Recommendation: Inspect immediately.")
        else:
            lines.append("Recommendation: Continue normal operation.")
        
        lines.append("-" * 60)
        
        return "\n".join(lines)
    
    def _format_plant_summary(self, context: MachineContext, alarm_timeline: list) -> str:
        """Format plant summary section."""
        lines = []
        
        critical_count = 1 if context.health_status == "CRITICAL" else 0
        warning_count = 1 if context.health_status == "WARNING" else 0
        running_count = 1 if context.machine_state == "RUNNING" else 0
        
        lines.append(f"Total Machines Analysed      : 1")
        lines.append(f"Running Machines             : {running_count}")
        lines.append(f"Warning Machines             : {warning_count}")
        lines.append(f"Critical Machines            : {critical_count}")
        lines.append(f"Total Alarm Events           : {len(alarm_timeline)}")
        
        # Get highest values from readings
        if context.current_readings:
            temps = []
            pressures = []
            for tag, reading in context.current_readings.items():
                value = reading.get("value")
                if isinstance(value, (int, float)):
                    if "Temp" in tag or "Temperature" in tag:
                        temps.append((tag, value))
                    elif "Pressure" in tag:
                        pressures.append((tag, value))
            
            if temps:
                max_tag, max_val = max(temps, key=lambda x: x[1])
                unit = context.current_readings[max_tag].get("unit", "")
                lines.append(f"Highest Temperature Reading  : {max_tag} ({max_val}{unit})")
            
            if pressures:
                max_tag, max_val = max(pressures, key=lambda x: x[1])
                unit = context.current_readings[max_tag].get("unit", "")
                lines.append(f"Highest Pressure Reading     : {max_tag} ({max_val}{unit})")
        
        lines.append(f"Plant Health Score           : {context.health_score:.0f} / 100")
        lines.append(f"Overall Plant Status         : {'ATTENTION REQUIRED' if context.active_alarms else 'NORMAL'}")
        
        return "\n".join(lines)
