"""Jinja2 templates for NLP story-based summarization."""
from jinja2 import Environment, Template

# Main narrative template
NLP_NARRATIVE_TEMPLATE = """================================================================================
MACHINE OPERATIONAL NARRATIVE REPORT
================================================================================

{% set health_adj = "excellent" if health_score >= 80 else "good" if health_score >= 60 else "concerning" %}
{% set health_status_text = "operating smoothly with " + health_adj + " health" if health_status in ["HEALTHY", "NORMAL"] else "experiencing challenges that require attention" %}

During the monitored period, the machine was found to be {{ health_status_text }}, with a health score of {{ health_score }}/100. The system is currently in a {{ machine_state | lower }} state and has been operating in this state for approximately {{ state_duration_seconds }} seconds.

SENSOR READINGS & OBSERVATIONS
--------------------------------------------------------------------------------
The machine's sensor array reveals the following operational picture:
{% for tag, reading in current_readings.items() %}
{% set trend_text = "showing upward movement" if reading.trend | lower == "increasing" else "showing downward movement" if reading.trend | lower == "decreasing" else "holding steady" if reading.trend | lower == "stable" else "displaying" %}
• {{ tag }} is at {% if reading.value is number %}{{ "%.2f" | format(reading.value) }}{% else %}{{ reading.value }}{% endif %}{{ reading.unit }}, currently {{ trend_text }}
{% endfor %}

{% if health_reasons %}
OPERATIONAL HEALTH ASSESSMENT
--------------------------------------------------------------------------------
The machine's health profile is determined by the following factors:
{% for reason in health_reasons %}
  • {{ reason }}
{% endfor %}

{% endif %}
{% if active_alarms %}
ALERTS & ANOMALIES DETECTED
--------------------------------------------------------------------------------
During this observation window, {{ active_alarms | length }} alarm(s) were triggered:
{% for alarm in active_alarms %}
{% set severity_map = {"critical": "CRITICAL", "high": "HIGH", "medium": "MEDIUM", "low": "LOW"} %}
{% set severity_display = severity_map.get(alarm.severity | lower, "MEDIUM") %}

Alarm #{{ loop.index }} [{{ severity_display }} Severity]:
  Time: {{ alarm.timestamp }}
  Issue: {{ alarm.tag }} reached {{ alarm.value }} (threshold: {{ alarm.threshold }})
  Details: {{ alarm.message }}
{% endfor %}

{% else %}
ALERT STATUS
--------------------------------------------------------------------------------
Good news - no alarms were triggered during the monitoring period. The machine operated without any threshold violations or critical events.

{% endif %}
{% set active_trends = namespace(items={}) %}
{% for tag, trend in trends.items() %}
{% if trend != "UNKNOWN" %}
{% set _ = active_trends.items.update({tag: trend}) %}
{% endif %}
{% endfor %}
{% if active_trends.items %}
TREND ANALYSIS
--------------------------------------------------------------------------------
Over the observation period, the following trends were observed:
{% for tag, trend in active_trends.items.items() %}
{% set trend_verb = "consistently rising" if trend == "INCREASING" else "consistently falling" if trend == "DECREASING" else "remaining stable" %}
  • {{ tag }} is {{ trend_verb }}
{% endfor %}

{% endif %}
STATISTICAL PERFORMANCE SUMMARY
--------------------------------------------------------------------------------
{% for tag, stats in statistics.items() %}
{{ tag }}:
  Range: {{ stats.min }} to {{ stats.max }}
  Average: {% if stats.mean is number %}{{ "%.2f" | format(stats.mean) }}{% else %}{{ stats.mean }}{% endif %}
{% endfor %}

{% if anomalies %}
UNUSUAL PATTERNS IDENTIFIED
--------------------------------------------------------------------------------
The system detected {{ anomalies | length }} anomalous behavior pattern(s):
{% for anomaly in anomalies %}
  • {{ anomaly.tag }}: {{ anomaly.type }}
    {{ anomaly.message }}
{% endfor %}

{% endif %}
RECOMMENDED ACTIONS
--------------------------------------------------------------------------------
{% if health_status == "CRITICAL" %}
[URGENT] IMMEDIATE ACTION REQUIRED:
The machine is operating at critical conditions. Immediate inspection and corrective maintenance should be scheduled as soon as possible to prevent equipment failure or damage.

{% endif %}
{% if active_alarms %}
• Investigate and resolve the {{ active_alarms | length }} active alarm(s) promptly.

{% endif %}
{% if anomalies %}
• Review the {{ anomalies | length }} anomalous pattern(s) identified and investigate root causes.

{% endif %}
{% if health_status == "WARNING" %}
• Schedule maintenance inspection within the next shift to address emerging issues.

{% elif health_status in ["HEALTHY", "NORMAL"] %}
• Continue regular monitoring and maintain current operational parameters.
• No immediate action required.

{% endif %}
CONCLUSION
--------------------------------------------------------------------------------
{% if health_status == "CRITICAL" %}
The machine requires immediate attention due to critical operational issues. Prioritize resolution of active alarms and schedule emergency maintenance.
{% elif health_status == "WARNING" %}
The machine is functioning but showing signs of degradation. Schedule preventive maintenance soon to maintain optimal performance.
{% else %}
The machine is operating normally with no critical issues. Continue standard monitoring procedures.
{% endif %}

================================================================================
Report Generated: {{ generated_at }}
================================================================================
"""
