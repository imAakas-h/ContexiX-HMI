"""Rule-based operator query parsing and boiler entity resolution."""
import re
from dataclasses import dataclass

from app.inputs.mock_fleet import BOILER_NAMES


@dataclass(frozen=True)
class OperatorQuery:
    machine: str
    intent: str


def resolve_query(text: str, default_machine: str = "Boiler-01") -> OperatorQuery:
    """Resolve a natural-language operator request without an external LLM."""
    normalized = text.lower()
    machine = default_machine
    if re.search(r"all\s+(machines|boilers)|every\s+(machine|boiler)", normalized):
        machine = "ALL"
    else:
        match = re.search(r"(?:boiler|unit|machine)\s*[- ]?(0?[1-3])", normalized)
        if match:
            machine = f"Boiler-{int(match.group(1)):02d}"
        elif re.search(r"first\s+boiler|boiler\s+one", normalized):
            machine = "Boiler-01"
        elif re.search(r"second\s+boiler|boiler\s+two", normalized):
            machine = "Boiler-02"
        elif re.search(r"third\s+boiler|boiler\s+three", normalized):
            machine = "Boiler-03"

    if re.search(r"full\s+summary|comprehensive|overview|summary", normalized):
        intent = "comprehensive"
    elif re.search(r"alarm|alert|trip|warning", normalized):
        intent = "alarms"
    elif re.search(r"health|safe|condition|well", normalized):
        intent = "health"
    else:
        intent = "telemetry"
    return OperatorQuery(machine, intent)