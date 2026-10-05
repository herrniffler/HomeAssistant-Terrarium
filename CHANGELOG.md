# Changelog

## 0.2.0

From pure monitoring to actual control: day/night, lights, cooling and misting.

### New
- **Day and night:** light times as `time` entities, a *Daytime* sensor and separate targets for day and night. The times can be set from an automation (`time.set_value`).
- **Transition:** after light on/off the limits glide linearly from the old phase to the new one over the adjustable *Transition: duration* (default 2 h). A terrarium cools down slowly in the evening, so that no longer raises a false alarm.
- **Gradient:** *warm side* and *cold side* roles with their own limits and a minimum gradient, plus the sensors *Temperature warm*, *Temperature cold* and *Gradient*.
- **Humidity:** air sensors drive the status (mean). Optional bottom sensors are only shown as *Humidity bottom*, so a wet substrate does not raise an alarm.
- **Light control:** switching on a schedule, exact to the second, with verification and retries. Also *Light: fault*, *Light: automation* and a *Light* entity that shows and switches the configured lights together.
- **Cooling:** the light stays off while the warm side is too hot. The state survives a restart.
- **Misting:** the misting switch stamps "last misted". *Misting: automation* mists by humidity, daytime only, with a minimum interval and adjustable duration.
- **Events:** `terrarium_event` (`cooling_started`, `cooling_ended`, `light_fault`, `light_fault_cleared`, `misting_started`) with name, species and values, for your own notifications.
- Logo and brand icons, README and changelog.

### Changed
- Entity names follow the pattern "Topic: property", and temperatures are named *Temperature warm/cold*. Entity IDs of existing devices stay unchanged.
- Species profiles now include night values and cold-side values, with more generous humidity maxima.

### Notes
- New settings take their defaults from the species profile only for newly added devices. For existing devices, adjust the numbers on the number entities.
- The values of the bundled species profiles are rough starting points (`"verified": false`).
- Temperatures are compared in °C.

## 0.1.0

First version: species profiles, targets for temperature and humidity, status, care log with buttons, feeding interval.
