"""Tests for the reference hysteresis controller."""

from custom_components.vtherm_hysteresis.hysteresis.controller import (
    HysteresisController,
)


def test_hysteresis_turns_on_below_lower_threshold() -> None:
    """Heating must start below the lower threshold."""
    controller = HysteresisController(hysteresis_on=0.3, hysteresis_off=0.5)

    on_percent = controller.calculate(target_temp=20.0, current_temp=19.7)

    assert on_percent == 1.0
    assert controller.is_heating is True
    assert controller.last_reason == "below_on_threshold"


def test_hysteresis_turns_off_above_upper_threshold() -> None:
    """Heating must stop above the upper threshold."""
    controller = HysteresisController(hysteresis_on=0.3, hysteresis_off=0.5)
    controller.restore_state({"is_heating": True, "last_reason": "manual"})

    on_percent = controller.calculate(target_temp=20.0, current_temp=20.5)

    assert on_percent == 0.0
    assert controller.is_heating is False
    assert controller.last_reason == "above_off_threshold"


def test_hysteresis_keeps_previous_state_inside_band() -> None:
    """The relay state must be preserved inside the hysteresis band."""
    controller = HysteresisController(hysteresis_on=0.3, hysteresis_off=0.5)
    controller.restore_state({"is_heating": True, "last_reason": "manual"})

    on_percent = controller.calculate(target_temp=20.0, current_temp=20.2)

    assert on_percent == 1.0
    assert controller.is_heating is True
    assert controller.last_reason == "hold_in_band"
