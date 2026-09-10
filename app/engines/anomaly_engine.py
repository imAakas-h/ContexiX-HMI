"""Anomaly detection engine - detects unusual patterns in machine data."""
from typing import Optional
from statistics import mean, stdev

from app.models.reading import MachineReading, MachineDataCollection


class AnomalyEngine:
    """Detects anomalies in machine readings."""
    
    ANOMALY_HIGH_VALUE = "HIGH_VALUE"
    ANOMALY_LOW_VALUE = "LOW_VALUE"
    ANOMALY_RATE_CHANGE = "RATE_OF_CHANGE"
    ANOMALY_OUTLIER = "OUTLIER"
    
    def __init__(self, config: dict = None):
        """
        Initialize anomaly engine.
        
        Args:
            config: Anomaly detection configuration
        """
        self.config = config or self._default_config()
        self.anomalies: list[dict] = []
    
    def _default_config(self) -> dict:
        """Default anomaly configuration."""
        return {
            "thresholds": {
                "Temperature": {"normal_min": 10, "normal_max": 80},
                "Pressure": {"normal_min": 0.5, "normal_max": 5.0},
                "MotorSpeed": {"normal_min": 1000, "normal_max": 2000},
                "MotorCurrent": {"normal_min": 2.0, "normal_max": 8.0},
                "Vibration": {"normal_min": 0.0, "normal_max": 0.5}
            },
            "std_deviation_threshold": 2.0  # 2 sigma
        }
    
    def detect_anomalies(
        self,
        collection: MachineDataCollection
    ) -> list[dict]:
        """
        Detect anomalies in collection.
        
        Args:
            collection: MachineDataCollection to analyze
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Group readings by tag
        readings_by_tag = self._group_by_tag(collection.readings)
        
        for tag, readings in readings_by_tag.items():
            if readings:
                tag_anomalies = self.detect_tag_anomalies(tag, readings)
                anomalies.extend(tag_anomalies)
        
        self.anomalies = anomalies
        return anomalies
    
    def detect_tag_anomalies(self, tag: str, readings: list[MachineReading]) -> list[dict]:
        """
        Detect anomalies for a single tag.
        
        Args:
            tag: Tag name
            readings: List of readings for this tag
            
        Returns:
            List of anomalies detected
        """
        anomalies = []
        latest_reading = readings[-1] if readings else None
        
        if not latest_reading or not isinstance(latest_reading.value, (int, float)):
            return anomalies
        
        value = latest_reading.value
        thresholds = self.config.get("thresholds", {}).get(tag)
        
        # Check against configured normal range
        if thresholds:
            if value > thresholds.get("normal_max"):
                anomalies.append({
                    "tag": tag,
                    "timestamp": latest_reading.timestamp,
                    "type": self.ANOMALY_HIGH_VALUE,
                    "severity": "WARNING",
                    "value": value,
                    "threshold": thresholds.get("normal_max"),
                    "message": f"{tag} is above normal range: {value}"
                })
            elif value < thresholds.get("normal_min"):
                anomalies.append({
                    "tag": tag,
                    "timestamp": latest_reading.timestamp,
                    "type": self.ANOMALY_LOW_VALUE,
                    "severity": "WARNING",
                    "value": value,
                    "threshold": thresholds.get("normal_min"),
                    "message": f"{tag} is below normal range: {value}"
                })
        
        # Check rate of change
        if len(readings) > 1:
            rate_anomaly = self._check_rate_of_change(tag, readings)
            if rate_anomaly:
                anomalies.append(rate_anomaly)
        
        # Statistical outlier detection
        numeric_values = [r.value for r in readings if isinstance(r.value, (int, float))]
        if len(numeric_values) > 2:
            outlier = self._check_outlier(tag, numeric_values, latest_reading)
            if outlier:
                anomalies.append(outlier)
        
        return anomalies
    
    def _check_rate_of_change(self, tag: str, readings: list[MachineReading]) -> Optional[dict]:
        """Check for excessive rate of change."""
        numeric_readings = [
            r for r in readings
            if isinstance(r.value, (int, float))
        ]
        
        if len(numeric_readings) < 2:
            return None
        
        first = numeric_readings[0].value
        last = numeric_readings[-1].value
        
        if first == 0:
            return None
        
        change_rate = abs((last - first) / first)
        
        # Flag if change > 50% in short period
        if change_rate > 0.5:
            return {
                "tag": tag,
                "timestamp": numeric_readings[-1].timestamp,
                "type": self.ANOMALY_RATE_CHANGE,
                "severity": "INFO",
                "rate": change_rate,
                "message": f"{tag} changed {change_rate*100:.1f}% in short period"
            }
        
        return None
    
    def _check_outlier(
        self,
        tag: str,
        values: list[float],
        latest_reading: MachineReading
    ) -> Optional[dict]:
        """Statistical outlier detection using standard deviation."""
        if len(values) < 3:
            return None
        
        mean_val = mean(values)
        std_val = stdev(values)
        
        if std_val == 0:
            return None
        
        latest_value = values[-1]
        z_score = abs((latest_value - mean_val) / std_val)
        threshold = self.config.get("std_deviation_threshold", 2.0)
        
        if z_score > threshold:
            return {
                "tag": tag,
                "timestamp": latest_reading.timestamp,
                "type": self.ANOMALY_OUTLIER,
                "severity": "INFO",
                "z_score": z_score,
                "value": latest_value,
                "mean": mean_val,
                "message": f"{tag} is a statistical outlier (z={z_score:.2f})"
            }
        
        return None
    
    def _group_by_tag(self, readings: list[MachineReading]) -> dict[str, list[MachineReading]]:
        """Group readings by tag, sorted by timestamp."""
        grouped = {}
        for reading in readings:
            if reading.tag not in grouped:
                grouped[reading.tag] = []
            grouped[reading.tag].append(reading)
        
        # Sort each group by timestamp
        for tag in grouped:
            grouped[tag].sort(key=lambda r: r.timestamp)
        
        return grouped
