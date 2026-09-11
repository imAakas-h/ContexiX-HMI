"""Dynamic autocomplete catalog for plant-operator telemetry searches."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Suggestion:
    """A ranked operator search suggestion."""
    text: str
    category: str
    icon: str

    @property
    def display(self) -> str:
        return f"{self.icon} [{self.category}]  {self.text}"


class SuggestEngine:
    """Ranks machine, metric, and intent phrases against typed keystrokes."""

    def __init__(self) -> None:
        self.catalog = (
            ("Boiler-01", "Machine", "■", ("boiler 1", "unit 1", "first boiler")),
            ("Boiler-02", "Machine", "■", ("boiler 2", "unit 2", "second boiler")),
            ("Boiler-03", "Machine", "■", ("boiler 3", "unit 3", "third boiler")),
            ("All Boilers", "Machine", "■", ("all machines", "all boilers", "every unit")),
            ("Temperature", "Metric", "◈", ("temp", "temperature", "heat")),
            ("Pressure", "Metric", "◈", ("pressure", "bar")),
            ("Motor Current", "Metric", "◈", ("motor current", "current", "amps")),
            ("Motor Speed", "Metric", "◈", ("motor speed", "speed", "rpm")),
            ("Vibration", "Metric", "◈", ("vibration", "mm/s")),
            ("Machine Status", "Metric", "◈", ("machine status", "status", "state")),
            ("Show active alarms on Boiler-02", "Intent", "!", ("active alarms", "alarms")),
            ("Check health status of Boiler-01", "Intent", "♥", ("health status", "safe", "health")),
            ("Find boilers with high vibration", "Intent", "!", ("high vibration",)),
            ("Show all machines running", "Intent", "▶", ("all machines running", "running")),
            ("Summary report for Boiler-03", "Intent", "≡", ("summary", "overview", "report")),
        )

    def suggest(self, text: str, limit: int = 7) -> list[Suggestion]:
        """Return prefix/substring matches, with prefix matches ranked first."""
        needle = " ".join(text.lower().split())
        if not needle:
            return []
        ranked = []
        for phrase, category, icon, aliases in self.catalog:
            searchable = (phrase.lower(), *aliases)
            matches = [value for value in searchable if needle in value]
            if not matches:
                continue
            rank = min(0 if value.startswith(needle) else 1 for value in matches)
            ranked.append((rank, len(phrase), Suggestion(phrase, category, icon)))
        ranked.sort(key=lambda item: (item[0], item[1], item[2].text))
        return [item[2] for item in ranked[:limit]]