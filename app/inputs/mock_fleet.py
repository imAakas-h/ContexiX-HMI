"""Deterministic standalone telemetry for the three-boiler operator view."""
from datetime import datetime, timedelta, timezone

from app.models.reading import MachineDataCollection, MachineReading, QualityStatus


BOILER_NAMES = ("Boiler-01", "Boiler-02", "Boiler-03")
NODE_IDS = {
    "Temperature": "ns=2;i=2",
    "Pressure": "ns=2;i=3",
    "MotorSpeed": "ns=2;i=4",
    "MotorCurrent": "ns=2;i=5",
    "Vibration": "ns=2;i=6",
    "MachineStatus": "ns=2;i=7",
}
UNITS = {
    "Temperature": "°C",
    "Pressure": "bar",
    "MotorSpeed": "RPM",
    "MotorCurrent": "A",
    "Vibration": "mm/s",
    "MachineStatus": "",
}


def generate_fleet(window_minutes: int = 10, samples: int = 20) -> dict[str, MachineDataCollection]:
    """Generate a rolling telemetry window for every configured boiler."""
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(minutes=window_minutes)
    fleet = {}

    for boiler in BOILER_NAMES:
        readings = []
        for index in range(samples):
            progress = index / max(samples - 1, 1)
            timestamp = start + (end - start) * progress
            values = _values_for(boiler, progress, index)
            for tag, value in values.items():
                readings.append(MachineReading(
                    timestamp=timestamp,
                    node_id=NODE_IDS[tag],
                    tag=tag,
                    value=value,
                    data_type="String" if tag == "MachineStatus" else "Float",
                    quality=QualityStatus.GOOD,
                    unit=UNITS[tag],
                    boiler=boiler,
                ))
        fleet[boiler] = MachineDataCollection(
            source="mock://contexix-plant",
            duration_seconds=window_minutes * 60,
            sampling_interval_seconds=max(1, window_minutes * 60 // max(samples - 1, 1)),
            start_time=start,
            end_time=end,
            readings=readings,
        )
    return fleet


def _values_for(boiler: str, progress: float, index: int) -> dict[str, object]:
    """Return a believable operating profile with gentle sensor variation."""
    wave = ((index % 5) - 2) / 10
    if boiler == "Boiler-01":
        return {
            "Temperature": round(72.0 + wave, 2), "Pressure": round(3.2 + wave / 10, 2),
            "MotorCurrent": round(5.4 + wave / 5, 2), "MotorSpeed": round(1450 + wave * 10, 1),
            "Vibration": round(0.22 + wave / 20, 3), "MachineStatus": "RUNNING",
        }
    if boiler == "Boiler-02":
        return {
            "Temperature": round(74 + 22 * progress + wave, 2), "Pressure": round(6.0 + 2.8 * progress, 2),
            "MotorCurrent": round(6.2 + progress, 2), "MotorSpeed": round(1510 + progress * 80, 1),
            "Vibration": round(0.34 + progress * 0.12, 3), "MachineStatus": "WARNING",
        }
    running = progress > 0.6
    return {
        "Temperature": round(28 + 8 * progress + wave, 2), "Pressure": round(1.1 + 0.3 * progress, 2),
        "MotorCurrent": round(2.4 + (1.2 if running else 0) + wave / 5, 2),
        "MotorSpeed": round(1200 + wave * 10 if running else 0, 1),
        "Vibration": round(0.15 + (0.07 if running else 0) + wave / 30, 3),
        "MachineStatus": "RUNNING" if running else "IDLE",
    }