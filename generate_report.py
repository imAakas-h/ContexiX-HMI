#!/usr/bin/env python3
"""Generate formatted report with alarm timeline from YOUR data."""
from datetime import datetime
import sys
import io

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.main import MachineContextEngine
from app.context.report_generator import ReportGenerator


def main():
    """Generate report from machine data."""
    execution_start = datetime.utcnow()
    
    print("Initializing Machine Context Engine...")
    
    engine = MachineContextEngine(
        config_file="config.yaml",
        node_metadata_json="nodesfile.json",
        node_metadata_xml="BoilerModel2.NodeSet2 (1).xml"
    )
    
    print("Processing machine data...")
    context = engine.process("machine_data_5min.json")
    
    # Build alarm timeline from all readings
    alarm_timeline = _extract_alarm_timeline(context, engine)
    
    # Generate report
    report_gen = ReportGenerator()
    report = report_gen.generate_full_report(
        context=context,
        alarm_timeline=alarm_timeline,
        execution_start=execution_start
    )
    
    print("\n" + report)
    
    # Save report
    with open("machine_context_report.txt", "w") as f:
        f.write(report)
    
    print(f"\n✓ Report saved to machine_context_report.txt")


def _extract_alarm_timeline(context, engine) -> list:
    """Extract alarm events from context and readings."""
    timeline = []
    
    # Add active alarms
    for alarm in context.active_alarms:
        timeline.append({
            "timestamp": alarm.get("timestamp"),
            "tag": alarm.get("tag"),
            "value": alarm.get("value"),
            "unit": context.current_readings.get(alarm.get("tag"), {}).get("unit", ""),
            "threshold": alarm.get("threshold"),
            "severity": alarm.get("severity"),
            "message": alarm.get("message")
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.get("timestamp", ""))
    
    return timeline


if __name__ == "__main__":
    main()
