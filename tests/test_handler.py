"""Tests for the hysteresis handler cycle forcing behavior."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.vtherm_hysteresis.handler import HysteresisHandler
from custom_components.vtherm_hysteresis.hysteresis.controller import HysteresisController


def _make_thermostat() -> MagicMock:
    """Create a minimal thermostat runtime mock for handler tests."""
    thermostat = MagicMock()
    thermostat.vtherm_hvac_mode = "heat"
    thermostat.target_temperature = 20.0
    thermostat.current_temperature = 20.0
    thermostat.cycle_scheduler = None
    thermostat.update_custom_attributes = MagicMock()
    thermostat.async_write_ha_state = MagicMock()
    thermostat.hass = MagicMock()
    thermostat.hass.async_create_task = MagicMock()
    return thermostat


@pytest.mark.asyncio
async def test_control_heating_forces_cycle_restart_below_lower_threshold() -> None:
    """A lower-threshold crossing must force an immediate new cycle."""
    thermostat = _make_thermostat()
    thermostat.current_temperature = 19.6
    scheduler = AsyncMock()

    controller = HysteresisController(hysteresis_on=0.3, hysteresis_off=0.5)
    handler = HysteresisHandler(thermostat)
    handler._controller = controller
    handler._scheduler = scheduler

    await handler.control_heating(force=False)

    scheduler.start_cycle.assert_awaited_once_with("heat", 1.0, force=True)
    assert handler.should_publish_intermediate() is True
    assert controller.is_heating is True
    assert controller.last_reason == "below_on_threshold"


@pytest.mark.asyncio
async def test_control_heating_forces_cycle_restart_above_upper_threshold() -> None:
    """An upper-threshold crossing must force an immediate new cycle."""
    thermostat = _make_thermostat()
    thermostat.current_temperature = 20.6
    scheduler = AsyncMock()

    controller = HysteresisController(hysteresis_on=0.3, hysteresis_off=0.5)
    controller.restore_state({"is_heating": True, "last_reason": "manual"})

    handler = HysteresisHandler(thermostat)
    handler._controller = controller
    handler._scheduler = scheduler

    await handler.control_heating(force=False)

    scheduler.start_cycle.assert_awaited_once_with("heat", 0.0, force=True)
    assert handler.should_publish_intermediate() is True
    assert controller.is_heating is False
    assert controller.last_reason == "above_off_threshold"
