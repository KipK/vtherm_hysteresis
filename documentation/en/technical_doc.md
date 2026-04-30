# Technical documentation

## Architecture

The repository mirrors the structure of a complete external algorithm integration:

- `__init__.py` registers the algorithm factory in `VThermAPI`
- `factory.py` exposes the identifier used by VT to instantiate the handler
- `handler.py` implements the runtime lifecycle expected by `InterfacePropAlgorithmHandler`
- `hysteresis/controller.py` contains the isolated control law
- `config_flow.py` provides global and per-thermostat configuration entries

## Interface contract

The handler implements the following methods from `vtherm_api.interfaces.InterfacePropAlgorithmHandler`:

- `init_algorithm`
- `async_added_to_hass`
- `async_startup`
- `remove`
- `control_heating`
- `on_state_changed`
- `on_scheduler_ready`
- `should_publish_intermediate`

Each method is kept in the scaffold even when the hysteresis use case does not need complex logic, so plugin developers can see where each extension point belongs.

## Scheduler interaction

The controller does not switch hardware directly. It computes an `on_percent` and forwards that request to the VT cycle scheduler:

- `max_on_percent` is sent when heating is active (default `1.0`)
- `min_on_percent` is sent when the controller is idle (default `0.0`)

Both values are configurable per thermostat so that users can, for example, cap heating power at 80 % or keep a valve slightly open when idle.
