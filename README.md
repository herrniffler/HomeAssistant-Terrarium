<picture>
  <source media="(prefers-color-scheme: dark)" srcset="custom_components/terrarium/brand/dark_logo@2x.png">
  <img alt="Terrarium" src="custom_components/terrarium/brand/logo@2x.png" height="64">
</picture>

# Terrarium for Home Assistant

Species profiles, target ranges, care log, light control and misting for each terrarium (the idea: OpenPlantbook, but for terrariums).

## Installation
- HACS → Custom repository (Integration), or copy `custom_components/terrarium` to `/config/custom_components/`
- Restart, then *Settings → Devices & services → Terrarium*

## Setup
When adding a terrarium (and later under *Configure*) you pick a species profile and, optionally:
- **Temperature sensors** (warm side or all) and **Cold-side temperature sensors** (for gradients)
- **Humidity sensors** (air) and optionally **Bottom humidity sensors**: only the air sensors drive status and misting. Bottom sensors often hang close to the wet substrate and are only shown as **Humidity bottom**.
- **Misting switch**: turning it on stamps "last misted"; required for automatic misting
- **Light switches**: switched according to the light times

Everything is optional. Without sensors the status shows "No data".

## Each terrarium becomes a device with
**Monitoring**
- **Status** (OK / Too hot / Too cold / Cold side too hot / Cold side too cold / No gradient / Too dry / Too humid / No data) and **Out of range**
- **Temperature warm** and **Humidity** (mean of the sensors, `min`/`max` as attributes); with a cold side also **Temperature cold** and **Gradient**
- **Targets** as `number` entities, pre-filled from the species profile: temperature and humidity min/max for day and night, feeding interval
- Humidity is checked as the **mean** of the air sensors against min/max. Bottom sensors (see above) do not count.

**Day and night**
- **Light: on / Light: off** (`time`): in between it is day, otherwise night. The status checks against the targets of the current phase. The **Daytime** sensor shows the phase.
- **Transition: duration** (default 2 hours, 0 = off): a terrarium cools down slowly in the evening and warms up slowly in the morning. So the limits do not jump at light on/off but glide linearly from the old to the new value over this time (e.g. in the evening the maximum temperature falls from the day to the night maximum). The `transition` attribute on the status shows the progress (0 to 1).
- The light times can be set by your own automation (`time.set_value`), e.g. from the sun position or the electricity price.

**Gradient (only with cold-side sensors)**
- By day **Temperature warm min/max (day)** applies to the warm side, plus **Temperature cold min/max (day)** and **Gradient: min** (warm minus cold, 0 = not checked).
- At night, when the sides level out, the night values apply to all sensors together and the gradient is not checked.
- Without cold-side sensors one range applies to all sensors.

**Care log**
- Last fed / shed / misted (`datetime`) plus buttons to stamp them
- **Feeding: due** and **Feeding: next**

**Light control** (with light switches)
- The switches follow the light times, exact to the second. After switching, the state is verified: 3 attempts 5 s apart, a 12 minute pause, 3 more attempts, then **Light: fault**.
- **Light: automation** turns this on or off.
- **Light** shows whether the configured light switches are on (all on = on) and switches them all together. This does not touch the automation: the state stays until the schedule steps in again at the next day/night change (or on cooling, changed light times or a restart). To switch freely for longer, turn the automation off.

**Cooling** (with light switches)
- If the warm side stays above **Cooling: above temperature** (0 = off) for 5 minutes, the light goes off (**Cooling: active**).
- It comes back on when the warm side is below that value and the difference to the coldest reading is smaller than **Cooling: max. difference**, for 10 minutes. A timeout after 4 hours and the end of the day also end cooling. The state survives a restart.

**Automatic misting** (with a misting switch)
- Switch **Misting: automation**: when it is on and the humidity is below **Misting: below humidity**, the misting switch is turned on for **Misting: duration** (daytime only). At least **Misting: minimum interval** passes between two runs; manual misting counts for that, too.

## Events for automations
The `terrarium_event` event has the fields `terrarium` (name), `species`, `entry_id` and `type`. Cooling events add `temperature` (warm side), light faults add `want_on` (`true` = switching on failed, `false` = switching off failed):
`cooling_started`, `cooling_ended`, `light_fault`, `light_fault_cleared`, `misting_started`.
Use them to build notifications; the integration does not send any itself.

## Custom species profiles
`/config/terrarium_species.json` (overrides/extends the bundled ones):

```json
{
  "my_animal": {
    "name": "Genus species", "common": "Common name",
    "temp_min": 20, "temp_max": 30,
    "humidity_min": 50, "humidity_max": 80,
    "feeding_interval": 3,
    "cold_temp_min": 20, "cold_temp_max": 26, "gradient_min": 3
  }
}
```

All fields except `name` are optional: `cold_temp_min`, `cold_temp_max`, `gradient_min` (cold side by day), and night values `temp_min_night`, `temp_max_night`, `humidity_min_night`, `humidity_max_night` (otherwise equal to the day values).

## Notes
- The bundled values are rough starting points (`"verified": false`); please check them against your own husbandry.
- Temperatures are compared in °C.
- Changing the species profile resets the targets to the profile values.
