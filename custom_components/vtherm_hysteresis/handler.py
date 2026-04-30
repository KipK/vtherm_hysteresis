"""Hysteresis algorithm handler for the plugin runtime."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import slugify

from .const import (
    CONF_HYSTERESIS_OFF,
    CONF_HYSTERESIS_ON,
    CONF_MAX_ON_PERCENT,
    CONF_MIN_ON_PERCENT,
    CONF_TARGET_VTHERM,
    DEFAULT_OPTIONS,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .hysteresis.controller import HysteresisController

if TYPE_CHECKING:
    from vtherm_api.interfaces import InterfaceCycleScheduler, InterfaceThermostatRuntime

_LOGGER = logging.getLogger(__name__)
VT_DOMAIN = "versatile_thermostat"


class HysteresisHandler:
    """Handler implementing the VT external proportional algorithm lifecycle."""

    def __init__(self, thermostat: "InterfaceThermostatRuntime") -> None:
        """Bind the handler to a VT thermostat runtime object."""
        self._thermostat = thermostat
        self._store: Store | None = None
        self._controller: HysteresisController | None = None
        self._should_publish_intermediate = True
        self._last_committed_on_percent = 0.0
        self._scheduler: InterfaceCycleScheduler | None = None
        self._applied_config_entry_id: str | None = None

    def init_algorithm(self) -> None:
        """Create the algorithm instance and prepare persistence.

        VT calls this method after constructing the handler. The handler can
        read runtime configuration here and instantiate its own controller.
        """
        thermostat = self._thermostat
        config, entry_to_apply = self._resolve_effective_config()
        self._applied_config_entry_id = (
            entry_to_apply.entry_id if entry_to_apply is not None else None
        )

        safe_name = slugify(thermostat.name)
        self._store = Store(thermostat.hass, STORAGE_VERSION, STORAGE_KEY.format(safe_name))
        self._controller = HysteresisController(
            hysteresis_on=float(config[CONF_HYSTERESIS_ON]),
            hysteresis_off=float(config[CONF_HYSTERESIS_OFF]),
            max_on_percent=float(config[CONF_MAX_ON_PERCENT]),
            min_on_percent=float(config[CONF_MIN_ON_PERCENT]),
        )
        thermostat.prop_algorithm = self._controller

    def _resolve_effective_config(self) -> tuple[dict[str, float], object]:
        """Return the merged configuration and the applied config entry."""
        thermostat = self._thermostat
        config: dict[str, float] = dict(DEFAULT_OPTIONS)

        plugin_entries = thermostat.hass.config_entries.async_entries(DOMAIN)
        matching_entry = next(
            (
                entry
                for entry in plugin_entries
                if entry.data.get(CONF_TARGET_VTHERM) == thermostat.unique_id
            ),
            None,
        )
        global_entry = next(
            (entry for entry in plugin_entries if entry.unique_id == DOMAIN),
            None,
        )
        entry_to_apply = matching_entry or global_entry
        if entry_to_apply is not None:
            config.update(entry_to_apply.data)
            config.update(entry_to_apply.options)

        return config, entry_to_apply

    def _get_target_device_id(self) -> str | None:
        """Return the HA device id for the target thermostat."""
        t = self._thermostat
        registry = er.async_get(t.hass)

        entity_id = getattr(t, "entity_id", None)
        if entity_id:
            reg_entry = registry.async_get(entity_id)
            if reg_entry is not None and reg_entry.device_id:
                return reg_entry.device_id

        entity_id = registry.async_get_entity_id(CLIMATE_DOMAIN, VT_DOMAIN, t.unique_id)
        if not entity_id:
            return None

        reg_entry = registry.async_get(entity_id)
        if reg_entry is not None and reg_entry.device_id:
            return reg_entry.device_id
        return None

    def _bind_config_entry_to_device(self) -> None:
        """Link the applied config entry to the target thermostat device."""
        if self._applied_config_entry_id is None:
            return
        device_id = self._get_target_device_id()
        if not device_id:
            return
        dr.async_get(self._thermostat.hass).async_update_device(
            device_id,
            add_config_entry_id=self._applied_config_entry_id,
        )

    def _unbind_config_entry_from_device(self) -> None:
        """Unlink the applied config entry from the target thermostat device."""
        if self._applied_config_entry_id is None:
            return
        device_id = self._get_target_device_id()
        if not device_id:
            return
        dr.async_get(self._thermostat.hass).async_update_device(
            device_id,
            remove_config_entry_id=self._applied_config_entry_id,
        )

    async def async_added_to_hass(self) -> None:
        """Restore persistent algorithm state.

        This hook is optional for a simple relay controller, but it is part of
        the contract and is useful to document how a plugin can keep state
        across Home Assistant restarts.
        """
        if self._store is None or self._controller is None:
            return

        try:
            data = await self._store.async_load()
            self._controller.restore_state(data)
            self._last_committed_on_percent = self._controller.on_percent
        except Exception as err:  # pragma: no cover - defensive logging path
            _LOGGER.error("%s - Failed to load Hysteresis state: %s", self._thermostat, err)

        self._bind_config_entry_to_device()

    async def async_startup(self) -> None:
        """Run startup actions after the thermostat is ready.

        SmartPI uses this hook for more advanced runtime coordination. The
        hysteresis example keeps it lightweight and simply aligns the handler
        with the current HVAC state.
        """
        await self.on_state_changed(True)

    def remove(self) -> None:
        """Release resources and persist the current controller state."""
        self._unbind_config_entry_from_device()
        thermostat = self._thermostat
        if self._store is not None and self._controller is not None:
            thermostat.hass.async_create_task(self._store.async_save(self._controller.save_state()))

    def on_scheduler_ready(self, scheduler: "InterfaceCycleScheduler") -> None:
        """Receive the VT cycle scheduler once it is available.

        Complex algorithms can register cycle callbacks here. The hysteresis
        example registers documented no-op callbacks so the scaffold shows where
        cycle start, cycle completion and realized power feedback are bridged.
        """
        self._scheduler = scheduler
        if self._controller is not None:
            scheduler.register_cycle_start_callback(self._controller.on_cycle_started)
            scheduler.register_cycle_end_callback(self._controller.on_cycle_completed)

    def should_publish_intermediate(self) -> bool:
        """Return True when VT may publish the current intermediate state."""
        return self._should_publish_intermediate

    async def control_heating(self, timestamp=None, force: bool = False) -> None:
        """Execute one control iteration.

        VT delegates all external proportional calculations to this method. The
        handler computes an `on_percent` and forwards it to the cycle scheduler.
        """
        del timestamp
        thermostat = self._thermostat
        controller = self._controller

        if controller is None:
            return

        previous_on_percent = controller.on_percent

        if str(thermostat.vtherm_hvac_mode).lower() == "off":
            controller.restore_state({"is_heating": False, "last_reason": "hvac_off"})
            self._should_publish_intermediate = previous_on_percent != 0.0

            if thermostat.is_device_active:
                await thermostat.async_underlying_entity_turn_off()
        else:
            controller.calculate(
                target_temp=thermostat.target_temperature,
                current_temp=thermostat.current_temperature,
            )
            self._should_publish_intermediate = (
                force or abs(controller.on_percent - previous_on_percent) > 0.001
            )

            scheduler = self._scheduler or thermostat.cycle_scheduler
            if scheduler is not None:
                await scheduler.start_cycle(
                    thermostat.vtherm_hvac_mode,
                    controller.on_percent,
                    force=force or self._should_publish_intermediate,
                )

        self._last_committed_on_percent = controller.on_percent
        thermostat.update_custom_attributes()
        thermostat.async_write_ha_state()

        if self._store is not None:
            thermostat.hass.async_create_task(self._store.async_save(controller.save_state()))

    async def on_state_changed(self, changed: bool) -> None:
        """React to thermostat state changes.

        SmartPI uses this for timers and learning state. The hysteresis example
        documents the same hook with a single behavior: request a fresh control
        iteration whenever VT changes a relevant state.
        """
        del changed
        await self._thermostat.async_control_heating(force=True)
