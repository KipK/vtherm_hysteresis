"""Discrete heating hysteresis controller used by the plugin handler."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HysteresisState:
    """Persisted state for the hysteresis controller."""

    is_heating: bool = False
    last_reason: str = "idle"


class HysteresisController:
    """Simple relay controller with separate on and off thresholds."""

    def __init__(
        self,
        hysteresis_on: float,
        hysteresis_off: float,
        state: HysteresisState | None = None,
    ) -> None:
        """Store the thresholds and initial relay state."""
        self._hysteresis_on = hysteresis_on
        self._hysteresis_off = hysteresis_off
        self._state = state or HysteresisState()

    @property
    def on_percent(self) -> float:
        """Return the duty request expected by the VT cycle scheduler."""
        return 1.0 if self._state.is_heating else 0.0

    @property
    def is_heating(self) -> bool:
        """Return the current relay state."""
        return self._state.is_heating

    @property
    def hysteresis_on(self) -> float:
        """Return the lower threshold distance used to start heating."""
        return self._hysteresis_on

    @property
    def hysteresis_off(self) -> float:
        """Return the upper threshold distance used to stop heating."""
        return self._hysteresis_off

    @property
    def last_reason(self) -> str:
        """Return a short explanation of the last state decision."""
        return self._state.last_reason

    def restore_state(self, data: dict[str, object] | None) -> None:
        """Restore the persisted relay state."""
        if not data:
            return

        is_heating = data.get("is_heating")
        if isinstance(is_heating, bool):
            self._state.is_heating = is_heating

        last_reason = data.get("last_reason")
        if isinstance(last_reason, str):
            self._state.last_reason = last_reason

    def save_state(self) -> dict[str, object]:
        """Serialize the relay state for Home Assistant storage."""
        return {
            "is_heating": self._state.is_heating,
            "last_reason": self._state.last_reason,
        }

    def calculate(
        self,
        target_temp: float | None,
        current_temp: float | None,
    ) -> float:
        """Apply the relay hysteresis law and return the resulting on_percent."""
        if target_temp is None or current_temp is None:
            self._state.is_heating = False
            self._state.last_reason = "missing_temperature"
            return self.on_percent

        turn_on_threshold = target_temp - self._hysteresis_on
        turn_off_threshold = target_temp + self._hysteresis_off

        if current_temp <= turn_on_threshold:
            self._state.is_heating = True
            self._state.last_reason = "below_on_threshold"
        elif current_temp >= turn_off_threshold:
            self._state.is_heating = False
            self._state.last_reason = "above_off_threshold"
        else:
            self._state.last_reason = "hold_in_band"

        return self.on_percent

    async def on_cycle_started(
        self,
        on_time_sec: float,
        off_time_sec: float,
        on_percent: float,
        hvac_mode: str,
    ) -> None:
        """Handle the cycle start callback exposed by the VT scheduler.

        The simple hysteresis example does not need cycle-start feedback, but
        the method is kept as a documented extension point because advanced
        controllers can use it to capture the command effectively committed by
        the scheduler at the beginning of a cycle.
        """
        del on_time_sec
        del off_time_sec
        del on_percent
        del hvac_mode

    async def on_cycle_completed(
        self,
        e_eff: float | None = None,
        elapsed_ratio: float = 1.0,
        cycle_duration_min: float | None = None,
        **_kw: object,
    ) -> None:
        """Handle the cycle completion callback exposed by the VT scheduler.

        SmartPI uses this hook to observe the effective power really applied on
        the cycle through `e_eff`. The hysteresis example does not consume that
        information, but the method is intentionally present so developers can
        document or extend the plugin around realized power feedback.
        """
        del e_eff
        del elapsed_ratio
        del cycle_duration_min
