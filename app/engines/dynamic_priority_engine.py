"""Priority, safety filtering, and adaptive widget layout for the operator HMI."""
from enum import Enum
from math import isfinite
from typing import Any

from pydantic import BaseModel, Field


class WidgetPlacement(str, Enum):
    """Adaptive destination for an operator action."""
    safety_panel = "safety_panel"
    tier_1_active = "tier_1_active"
    tier_2_secondary = "tier_2_secondary"
    tier_3_memory_store = "tier_3_memory_store"


class ControlType(str, Enum):
    """Supported operator control types."""
    ActionButton = "ActionButton"
    ToggleSwitch = "ToggleSwitch"
    Slider = "Slider"
    KnobStepper = "KnobStepper"


class BoilerActionWidget(BaseModel):
    """A prioritized action exposed by a boiler asset."""
    action_id: str
    asset_id: str = Field(pattern=r"^Boiler_[12]$")
    name: str
    control_type: ControlType
    node_id: str
    frequency: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    hazardness: float = Field(ge=0.0, le=1.0)
    is_safety_critical: bool
    priority_score: float = Field(default=0.0, ge=0.0, le=1.0)
    placement: WidgetPlacement = WidgetPlacement.tier_3_memory_store
    ui_coordinates: dict[str, Any] = Field(default_factory=dict)


class DynamicPriorityEngine:
    """Ranks actions and emits a JSON-ready adaptive layout schema."""

    def __init__(
        self,
        weight_hazard: float = 0.50,
        weight_recency: float = 0.30,
        weight_frequency: float = 0.20,
    ) -> None:
        self.weight_hazard = weight_hazard
        self.weight_recency = weight_recency
        self.weight_frequency = weight_frequency
        self.registry = self._seed_registry()

    def _seed_registry(self) -> dict[str, BoilerActionWidget]:
        boiler_1 = [
            ("emergency_steam_dump", "Open Emergency Steam Dump", ControlType.ActionButton, 0.92, 0.90, 0.98, True),
            ("aux_feedwater_override", "Enable Aux Feedwater Override", ControlType.ToggleSwitch, 0.74, 0.75, 0.90, True),
            ("drum_level_trim", "Set Drum Level Trim", ControlType.Slider, 0.62, 0.58, 0.72, False),
            ("primary_burner_cutoff", "Trip Primary Burner", ControlType.ActionButton, 0.55, 0.82, 0.96, True),
            ("fd_fan_trim", "Trim FD Fan Speed", ControlType.KnobStepper, 0.46, 0.50, 0.61, False),
            ("continuous_blowdown", "Set Continuous Blowdown", ControlType.Slider, 0.31, 0.40, 0.50, False),
            ("deaerator_sparge", "Enable Deaerator Sparge", ControlType.ToggleSwitch, 0.25, 0.32, 0.44, False),
            ("sootblower_cycle", "Start Sootblower Cycle", ControlType.ActionButton, 0.19, 0.25, 0.35, False),
            ("chemical_dose_pump", "Set Chemical Dose Pump", ControlType.KnobStepper, 0.12, 0.18, 0.28, False),
            ("lab_sample_purge", "Start Lab Sample Purge", ControlType.ActionButton, 0.06, 0.10, 0.18, False),
        ]
        boiler_2 = [
            ("master_fuel_trip", "Execute Master Fuel Trip", ControlType.ActionButton, 0.88, 0.86, 1.00, True),
            ("superheat_attemperator", "Set Superheat Attemperator", ControlType.Slider, 0.68, 0.70, 0.82, False),
            ("combustion_ratio_trim", "Trim Combustion Ratio", ControlType.KnobStepper, 0.57, 0.62, 0.70, False),
            ("quick_sludge_blowdown", "Open Quick Sludge Blowdown", ControlType.ActionButton, 0.49, 0.53, 0.66, False),
            ("id_fan_vfd_trim", "Set ID Fan VFD Speed", ControlType.Slider, 0.39, 0.43, 0.58, False),
            ("recirc_pump", "Start Recirculation Pump", ControlType.ToggleSwitch, 0.34, 0.36, 0.52, False),
            ("pilot_igniter", "Ignite Pilot Burner", ControlType.ActionButton, 0.27, 0.30, 0.48, False),
            ("stack_damper_lock", "Lock Stack Damper", ControlType.ToggleSwitch, 0.20, 0.22, 0.43, False),
            ("o2_analyzer_zero", "Zero O2 Analyzer", ControlType.KnobStepper, 0.14, 0.16, 0.31, False),
            ("skid_lighting", "Switch Skid Lighting", ControlType.ToggleSwitch, 0.08, 0.08, 0.12, False),
        ]
        registry: dict[str, BoilerActionWidget] = {}
        for asset_number, actions in ((1, boiler_1), (2, boiler_2)):
            for name, label, control_type, frequency, recency, hazardness, safety in actions:
                action_id = f"boiler_{asset_number}_{name}"
                registry[action_id] = BoilerActionWidget(
                    action_id=action_id,
                    asset_id=f"Boiler_{asset_number}",
                    name=label,
                    control_type=control_type,
                    node_id=f"ns=2;s={action_id}",
                    frequency=frequency,
                    recency=recency,
                    hazardness=hazardness,
                    is_safety_critical=safety,
                )
        return registry

    def apply_time_decay(self, elapsed_minutes: float) -> None:
        """Decay recency using the configured heuristic and clamp invalid input."""
        if not isfinite(elapsed_minutes) or elapsed_minutes < 0:
            raise ValueError("elapsed_minutes must be a finite non-negative number")
        decay_lambda = 0.02
        multiplier = max(0.0, 1.0 - decay_lambda * elapsed_minutes)
        for widget in self.registry.values():
            widget.recency = max(0.0, min(1.0, widget.recency * multiplier))

    def evaluate_priorities_and_layout(self) -> dict[str, Any]:
        """Calculate scores and return the complete dynamic UI schema."""
        safety_panel = []
        tier_1 = []
        tier_2 = []
        tier_3 = []
        overflow = []
        non_safety = [widget for widget in self.registry.values() if not widget.is_safety_critical]
        non_safety.sort(
            key=lambda widget: (
                self.weight_hazard * widget.hazardness
                + self.weight_recency * widget.recency
                + self.weight_frequency * widget.frequency
            ),
            reverse=True,
        )
        ranked_ids = {widget.action_id: index for index, widget in enumerate(non_safety)}
        for widget in self.registry.values():
            widget.priority_score = round(
                self.weight_hazard * widget.hazardness
                + self.weight_recency * widget.recency
                + self.weight_frequency * widget.frequency,
                4,
            )
            if widget.is_safety_critical:
                widget.placement = WidgetPlacement.safety_panel
                widget.ui_coordinates = {"region": "persistent_safety_toolbar", "locked": True}
                safety_panel.append(widget)
            else:
                rank = ranked_ids[widget.action_id]
                if rank < 4:
                    widget.placement = WidgetPlacement.tier_1_active
                    index = len(tier_1)
                    widget.ui_coordinates = {"row": index // 4, "col": index % 4, "grid_area": f"r{index // 4}c{index % 4}"}
                    tier_1.append(widget)
                elif rank < 7:
                    widget.placement = WidgetPlacement.tier_2_secondary
                    widget.ui_coordinates = {"drawer": "quick_actions", "tab": len(tier_2) + 1, "collapsed": False}
                    tier_2.append(widget)
                elif rank < 9:
                    widget.placement = WidgetPlacement.tier_3_memory_store
                    widget.ui_coordinates = {"search_index": f"{widget.asset_id}:{widget.name.lower()}", "archive": True}
                    tier_3.append(widget)
                else:
                    widget.placement = WidgetPlacement.tier_3_memory_store
                    widget.ui_coordinates = {"search_index": f"{widget.asset_id}:{widget.name.lower()}", "archive": True, "overflow": True}
                    overflow.append(widget)

        tier_1.sort(key=lambda item: item.priority_score, reverse=True)
        tier_2.sort(key=lambda item: item.priority_score, reverse=True)
        tier_3.sort(key=lambda item: item.priority_score, reverse=True)
        for index, widget in enumerate(tier_1):
            widget.ui_coordinates = {
                "row": index // 4,
                "col": index % 4,
                "grid_area": f"r{index // 4}c{index % 4}",
            }

        serialize = lambda items: [item.model_dump(mode="json") for item in items]
        return {
            "schema_version": "1.0",
            "weights": {"hazardness": self.weight_hazard, "recency": self.weight_recency, "frequency": self.weight_frequency},
            "safety_toolbar": {"screen_share_target": "10-15%", "locked": True, "widgets": serialize(safety_panel)},
            "tier_1_grid": {"layout": "css-grid", "columns": 4, "widgets": serialize(tier_1)},
            "tier_2_drawers": {"drawer_id": "quick_actions", "widgets": serialize(tier_2)},
            "tier_3_memory_store": {"search_only": True, "widgets": serialize(tier_3)},
            "overflow_archive": {"search_only": True, "widgets": serialize(overflow)},
        }

    def record_operator_interaction(self, action_id: str) -> dict[str, Any]:
        """Reset recency, increase frequency, and return the updated layout."""
        widget = self.registry.get(action_id)
        if widget is None:
            raise KeyError(f"Unknown action: {action_id}")
        widget.recency = 1.0
        widget.frequency = min(1.0, round(widget.frequency + 0.05, 4))
        return self.evaluate_priorities_and_layout()