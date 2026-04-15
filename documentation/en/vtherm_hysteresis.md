# Hysteresis

## Purpose

This integration exposes a basic heating hysteresis controller to Versatile Thermostat through the external algorithm API.

It is intentionally simple and is meant to serve as a reference implementation for developers who want to plug another algorithm into VT.

## Parameters

### Heating restart delta

When the room temperature drops below `target - hysteresis_on`, the controller requests heating.

### Heating stop delta

When the room temperature rises above `target + hysteresis_off`, the controller requests stop.

## Configuration modes

The config flow supports two scopes:

- global defaults applied when no thermostat-specific plugin entry exists
- thermostat-specific settings bound to one VT entity

## Persistence

The relay state is stored in Home Assistant storage so the controller can resume with a consistent band state after a restart.
