"""Trend engine - calculates statistics and trends for sensor values."""
from datetime import datetime, timedelta
from typing import Optional
from statistics import mean, stdev

from app.models.reading import MachineReading, MachineDataCollection


class TrendEngine:
    """Calculates trends and statistics for machine readings."""
    
    TREND_INCREASING = "INCREASING"
    TREND_DECREASING = "DECREASING"
    TREND_STABLE = "STABLE"
    TREND_UNKNOWN = "UNKNOWN"
    
    def __init__(self, config: dict = None):
        """
        Initialize trend engine.
        
        Args:
            config: Configuration for trend detection
        """
        self.config = config or self._default_config()
        self.trends: dict[str, dict] = {}
    
    def _default_config(self) -> dict:
        """Default trend configuration."""
        return {
            "trend_window_seconds": 60,  # Look at last minute
            "stable_threshold": 0.05  # 5% change is stable
        }
    
    def calculate_trends(self, collection: MachineDataCollection) -> dict[str, dict]:
        """
        Calculate trends for all readings.
        
        Args:
            collection: MachineDataCollection with readings
            
        Returns:
            Dict of tag -> trend info
        """
        trends = {}
        
        # Group readings by tag
        readings_by_tag = self._group_by_tag(collection.readings)
        
        for tag, readings in readings_by_tag.items():
            if readings:
                trend_info = self.analyze_trend(tag, readings)
                trends[tag] = trend_info
        
        self.trends = trends
        return trends
    
    def analyze_trend(self, tag: str, readings: list[MachineReading]) -> dict:
        """
        Analyze trend for a single tag.
        
        Args:
            tag: Tag name
            readings: List of readings for this tag (sorted by timestamp)
            
        Returns:
            Dict with trend analysis
        """
        # Extract numeric values
        values = [r.value for r in readings if isinstance(r.value, (int, float))]
        
        if len(values) < 2:
            return {
                "tag": tag,
                "trend": self.TREND_UNKNOWN,
                "direction": "unknown",
                "current": values[0] if values else None,
                "min": values[0] if values else None,
                "max": values[0] if values else None,
                "mean": values[0] if values else None,
                "std": 0,
                "rate_of_change": 0,
                "samples": len(values)
            }
        
        # Calculate statistics
        current = values[-1]
        min_val = min(values)
        max_val = max(values)
        mean_val = mean(values)
        std_val = stdev(values) if len(values) > 1 else 0
        
        # Calculate rate of change
        rate_of_change = self._calculate_rate_of_change(values)
        
        # Determine trend
        trend_direction = self._determine_trend(values)
        
        return {
            "tag": tag,
            "trend": trend_direction,
            "direction": "up" if rate_of_change > 0 else "down" if rate_of_change < 0 else "stable",
            "current": current,
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
            "std": std_val,
            "rate_of_change": rate_of_change,
            "samples": len(values)
        }
    
    def _calculate_rate_of_change(self, values: list[float]) -> float:
        """Calculate rate of change across values."""
        if len(values) < 2:
            return 0
        
        first = values[0]
        last = values[-1]
        
        if first == 0:
            return 0
        
        return (last - first) / first
    
    def _determine_trend(self, values: list[float]) -> str:
        """Determine if trend is INCREASING, DECREASING, or STABLE."""
        if len(values) < 2:
            return self.TREND_UNKNOWN
        
        first = values[0]
        last = values[-1]
        
        if first == 0:
            return self.TREND_UNKNOWN
        
        change_percent = abs((last - first) / first)
        stable_threshold = self.config.get("stable_threshold", 0.05)
        
        if change_percent < stable_threshold:
            return self.TREND_STABLE
        elif last > first:
            return self.TREND_INCREASING
        else:
            return self.TREND_DECREASING
    
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
    
    def get_trend(self, tag: str) -> Optional[dict]:
        """Get trend for a specific tag."""
        return self.trends.get(tag)
