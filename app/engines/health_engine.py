"""Machine health engine - calculates overall machine health status."""
from typing import Optional

from app.models.context import MachineHealth
from app.models.event import MachineEvent, Severity


class HealthEngine:
    """Calculates machine health from alarms, anomalies, and state."""
    
    def __init__(self, config: dict = None):
        """
        Initialize health engine.
        
        Args:
            config: Health calculation configuration
        """
        self.config = config or self._default_config()
    
    def _default_config(self) -> dict:
        """Default health configuration."""
        return {
            "scoring": {
                "critical_alarm": -25,
                "warning_alarm": -8,
                "anomaly": -5,
                "degraded_quality": -5
            },
            "thresholds": {
                "critical": 30,   # Score below this = CRITICAL
                "warning": 60,    # Score below this = WARNING
                "normal": 80      # Score below this = NORMAL
            }
        }
    
    def calculate_health(
        self,
        active_alarms: list[MachineEvent] = None,
        anomalies: list[dict] = None,
        communication_quality: float = 1.0,
        machine_state: str = None
    ) -> tuple[str, float, list[str]]:
        """
        Calculate overall machine health.
        
        Args:
            active_alarms: List of active alarms
            anomalies: List of detected anomalies
            communication_quality: Quality 0-1
            machine_state: Current machine state
            
        Returns:
            Tuple of (health_status, score, reasons)
        """
        active_alarms = active_alarms or []
        anomalies = anomalies or []
        
        score = 100.0
        reasons = []
        
        # Deduct for critical alarms
        critical_alarms = [a for a in active_alarms if a.severity == Severity.CRITICAL]
        if critical_alarms:
            deduction = len(critical_alarms) * self.config["scoring"]["critical_alarm"]
            score += deduction
            reasons.append(f"{len(critical_alarms)} critical alarm(s)")
        
        # Deduct for warning alarms
        warning_alarms = [a for a in active_alarms if a.severity == Severity.WARNING]
        if warning_alarms:
            deduction = len(warning_alarms) * self.config["scoring"]["warning_alarm"]
            score += deduction
            reasons.append(f"{len(warning_alarms)} warning alarm(s)")
        
        # Deduct for anomalies
        if anomalies:
            deduction = len(anomalies) * self.config["scoring"]["anomaly"]
            score += deduction
            reasons.append(f"{len(anomalies)} anomaly/ies detected")
        
        # Deduct for poor communication quality
        if communication_quality < 0.8:
            deduction = (1.0 - communication_quality) * self.config["scoring"]["degraded_quality"]
            score -= deduction
            reasons.append(f"Communication quality: {communication_quality*100:.0f}%")
        
        # Deduct for offline/stopped state
        if machine_state in ["OFFLINE", "FAULT", "MAINTENANCE"]:
            score -= 20
            reasons.append(f"Machine state: {machine_state}")
        
        # Clamp score to 0-100
        score = max(0, min(100, score))
        
        # Determine health status
        thresholds = self.config["thresholds"]
        if score >= thresholds["normal"]:
            health = MachineHealth.HEALTHY
        elif score >= thresholds["warning"]:
            health = MachineHealth.NORMAL
        elif score >= thresholds["critical"]:
            health = MachineHealth.WARNING
        else:
            health = MachineHealth.CRITICAL
        
        return health, score, reasons
