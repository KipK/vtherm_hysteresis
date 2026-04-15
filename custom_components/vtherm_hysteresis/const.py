"""Constants for the vtherm_hysteresis integration."""

from __future__ import annotations

DOMAIN = "vtherm_hysteresis"
NAME = "Versatile Thermostat Hysteresis"

CONF_TARGET_VTHERM = "target_vtherm_unique_id"
CONF_PROP_FUNCTION = "proportional_function"
CONF_HYSTERESIS_ON = "hysteresis_on"
CONF_HYSTERESIS_OFF = "hysteresis_off"

DEFAULT_HYSTERESIS_ON = 0.3
DEFAULT_HYSTERESIS_OFF = 0.3

DEFAULT_OPTIONS: dict[str, float] = {
    CONF_HYSTERESIS_ON: DEFAULT_HYSTERESIS_ON,
    CONF_HYSTERESIS_OFF: DEFAULT_HYSTERESIS_OFF,
}

PROP_FUNCTION_HYSTERESIS = "hysteresis"

DATA_FACTORY_REGISTERED = "factory_registered"

STORAGE_VERSION = 1
STORAGE_KEY = "vtherm_hysteresis.{}"
