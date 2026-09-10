"""Configuration management."""
import yaml
from pathlib import Path
from typing import Optional, Any


class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to config.yaml (optional)
        """
        self.data = self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[str]) -> dict:
        """Load configuration from YAML file."""
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return self._default_config()
    
    def _default_config(self) -> dict:
        """Default configuration."""
        return {
            "machine": {
                "name": "Industrial Machine"
            },
            "engines": {
                "state": {},
                "alarm": {
                    "thresholds": {
                        "Temperature": {"high": 85.0, "low": 5.0},
                        "Pressure": {"high": 8.0, "low": 0.5},
                        "MotorSpeed": {"high": 2000.0, "low": 0.0},
                        "MotorCurrent": {"high": 10.0, "low": 0.0},
                        "Vibration": {"high": 1.0, "low": 0.0}
                    }
                },
                "trend": {},
                "anomaly": {
                    "thresholds": {
                        "Temperature": {"normal_min": 10, "normal_max": 80},
                        "Pressure": {"normal_min": 0.5, "normal_max": 5.0},
                        "MotorSpeed": {"normal_min": 1000, "normal_max": 2000},
                        "MotorCurrent": {"normal_min": 2.0, "normal_max": 8.0},
                        "Vibration": {"normal_min": 0.0, "normal_max": 0.5}
                    }
                },
                "health": {}
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
