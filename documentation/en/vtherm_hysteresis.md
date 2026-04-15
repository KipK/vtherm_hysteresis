# Hysteresis

## Purpose

This integration exposes a basic heating hysteresis controller to Versatile Thermostat through the external algorithm API.

It is intentionally simple and is meant to serve as a reference implementation for developers who want to plug another algorithm into VT.

## Parameters

### Heating restart delta

When the room temperature drops below `target - hysteresis_on`, the controller requests heating.

### Heating stop delta

When the room temperature rises above `target + hysteresis_off`, the controller requests stop.

### Maximum heating power (`max_on_percent`)

The maximum duty-cycle fraction sent to the cycle scheduler when heating is active. A value of `1.0` means 100 % (default). Reduce this for radiators with high thermal inertia to avoid overshooting the target temperature, or to limit valve opening in heating mode.

Range: `0.0` – `1.0`. Default: `1.0`.

### Minimum cooling power (`min_on_percent`)

The duty-cycle fraction sent to the cycle scheduler when the controller is idle (not heating). A value of `0.0` means completely off (default). Set a non-zero value to keep a valve partially open in cooling or idle mode.

Range: `0.0` – `1.0`. Default: `0.0`.

## Configuration modes

The config flow supports two scopes:

- global defaults applied when no thermostat-specific plugin entry exists
- thermostat-specific settings bound to one VT entity

## Persistence

The relay state is stored in Home Assistant storage so the controller can resume with a consistent band state after a restart.
