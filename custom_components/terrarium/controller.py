"""Runtime state and logic for a single terrarium."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_HUMIDITY_SENSORS,
    CONF_LIGHT_SWITCHES,
    CONF_MISTING_SWITCH,
    CONF_TEMPERATURE_SENSORS,
    DEFAULT_LIGHT_TIMES,
    DOMAIN,
    EVENT_KEYS,
    EVENT_TERRARIUM,
    GENERIC_DEFAULTS,
    LIGHT_RETRY_DELAY,
    LIGHT_RETRY_PAUSE,
    LIGHT_TIME_KEYS,
    LIGHT_TRIES,
    LIGHT_TRIES_BEFORE_PAUSE,
    SETPOINT_KEYS,
    STATUS_NO_DATA,
    STATUS_OK,
    STATUS_TOO_COLD,
    STATUS_TOO_DRY,
    STATUS_TOO_HOT,
    STATUS_TOO_HUMID,
    STORE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class TerrariumController:
    """Holds target values, care log and evaluates sensor readings."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        species_id: str,
        profile: dict[str, Any],
        config: dict[str, Any],
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.species_id = species_id
        self.profile = profile
        self.temperature_sensors: list[str] = list(
            config.get(CONF_TEMPERATURE_SENSORS, [])
        )
        self.humidity_sensors: list[str] = list(config.get(CONF_HUMIDITY_SENSORS, []))
        self.misting_switch: str | None = config.get(CONF_MISTING_SWITCH)
        self.light_switches: list[str] = list(config.get(CONF_LIGHT_SWITCHES, []))
        self.light_automation = True
        self.light_fault = False
        self._light_task: asyncio.Task[None] | None = None
        self.signal = f"{DOMAIN}_update_{entry.entry_id}"
        self.setpoints: dict[str, float] = {}
        self.events: dict[str, datetime | None] = dict.fromkeys(EVENT_KEYS)
        self.light_times: dict[str, time] = {}
        self._store: Store[dict[str, Any]] = Store(
            hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._last_due = False
        self._last_day = True
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Terrarium",
            model=profile.get("name", "Custom"),
        )

    # ------------------------------------------------------------------ setup

    async def async_load(self) -> None:
        """Load persisted values; reset targets if the species changed."""
        stored = await self._store.async_load() or {}

        defaults = dict(GENERIC_DEFAULTS)
        for key in SETPOINT_KEYS:
            if key in self.profile:
                defaults[key] = float(self.profile[key])
            elif key.endswith("_night"):
                # Day keys come first in SETPOINT_KEYS, so they are resolved already
                defaults[key] = defaults[key.removesuffix("_night")]

        saved: dict[str, Any] = {}
        if stored.get("species") == self.species_id:
            saved = stored.get("setpoints", {})
        self.setpoints = {k: float(saved.get(k, defaults[k])) for k in SETPOINT_KEYS}

        for key in LIGHT_TIME_KEYS:
            raw = stored.get("light_times", {}).get(key) or DEFAULT_LIGHT_TIMES[key]
            self.light_times[key] = dt_util.parse_time(raw) or dt_util.parse_time(
                DEFAULT_LIGHT_TIMES[key]
            )

        self.light_automation = bool(stored.get("light_automation", True))

        for key in EVENT_KEYS:
            raw = stored.get("events", {}).get(key)
            self.events[key] = dt_util.parse_datetime(raw) if raw else None

        self._last_due = self.feeding_due
        self._last_day = self.is_day

    @callback
    def async_start(self) -> None:
        """Start listening to source sensors and the feeding timer."""
        sensors = [*self.temperature_sensors, *self.humidity_sensors]
        if sensors:
            self.entry.async_on_unload(
                async_track_state_change_event(
                    self.hass, sensors, self._handle_source_change
                )
            )
        if self.misting_switch:
            self.entry.async_on_unload(
                async_track_state_change_event(
                    self.hass, [self.misting_switch], self._handle_misting_change
                )
            )
        self.entry.async_on_unload(
            async_track_time_interval(self.hass, self._handle_tick, timedelta(minutes=1))
        )
        if self.light_switches:
            # Bring the lights in line with the schedule once HA is up
            self.entry.async_on_unload(async_at_started(self.hass, self._started))

    async def async_flush(self) -> None:
        """Persist immediately (used on unload)."""
        await self._store.async_save(self._data_to_save())

    # --------------------------------------------------------------- readings

    def _readings(self, entity_ids: list[str]) -> list[float]:
        values: list[float] = []
        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                continue
            try:
                values.append(float(state.state))
            except ValueError:
                continue
        return values

    def reading_summary(self, entity_ids: list[str]) -> dict[str, float] | None:
        """Mean/min/max over the currently available readings, or None."""
        values = self._readings(entity_ids)
        if not values:
            return None
        return {
            "mean": round(sum(values) / len(values), 1),
            "min": min(values),
            "max": max(values),
        }

    @property
    def is_day(self) -> bool:
        """True between the light-on and light-off time (wraps over midnight)."""
        on, off = self.light_times["light_on"], self.light_times["light_off"]
        now = dt_util.now().time()
        if on == off:
            return True
        if on < off:
            return on <= now < off
        return now >= on or now < off

    def active_setpoint(self, key: str) -> float:
        """Setpoint for the current phase (day value or its night counterpart)."""
        return self.setpoints[key if self.is_day else f"{key}_night"]

    @property
    def problems(self) -> list[str]:
        """Active problems, most severe first."""
        result: list[str] = []
        temps = self._readings(self.temperature_sensors)
        if temps:
            if max(temps) > self.active_setpoint("temp_max"):
                result.append(STATUS_TOO_HOT)
            if min(temps) < self.active_setpoint("temp_min"):
                result.append(STATUS_TOO_COLD)
        hums = self._readings(self.humidity_sensors)
        if hums:
            if min(hums) < self.active_setpoint("humidity_min"):
                result.append(STATUS_TOO_DRY)
            if max(hums) > self.active_setpoint("humidity_max"):
                result.append(STATUS_TOO_HUMID)
        return result

    @property
    def status(self) -> str:
        if not (
            self._readings(self.temperature_sensors)
            or self._readings(self.humidity_sensors)
        ):
            return STATUS_NO_DATA
        problems = self.problems
        return problems[0] if problems else STATUS_OK

    @property
    def next_feeding(self) -> datetime | None:
        interval = self.setpoints["feeding_interval"]
        last = self.events["last_fed"]
        if last is None or interval <= 0:
            return None
        return last + timedelta(days=interval)

    @property
    def feeding_due(self) -> bool:
        nxt = self.next_feeding
        return nxt is not None and dt_util.utcnow() >= nxt

    # ---------------------------------------------------------------- changes

    @callback
    def async_set_setpoint(self, key: str, value: float) -> None:
        self.setpoints[key] = float(value)
        self._changed()

    @callback
    def async_set_event(self, key: str, value: datetime | None) -> None:
        self.events[key] = value
        self._changed()

    @callback
    def async_set_light_time(self, key: str, value: time) -> None:
        self.light_times[key] = value
        self._changed()
        self._schedule_light_sync()

    @callback
    def async_set_light_automation(self, value: bool) -> None:
        self.light_automation = value
        self._changed()
        self._schedule_light_sync()

    # ------------------------------------------------------------------ light

    @callback
    def _fire_event(self, event_type: str) -> None:
        """Fire a bus event that automations can use for notifications."""
        self.hass.bus.async_fire(
            EVENT_TERRARIUM,
            {
                "entry_id": self.entry.entry_id,
                "terrarium": self.entry.title,
                "type": event_type,
            },
        )

    @callback
    def _started(self, hass: HomeAssistant) -> None:
        self._schedule_light_sync()

    @callback
    def _schedule_light_sync(self) -> None:
        """(Re)start the task that brings the lights in line with the schedule."""
        if self._light_task is not None and not self._light_task.done():
            self._light_task.cancel()
        if not (self.light_switches and self.light_automation):
            self._set_light_fault(False)
            return
        self._light_task = self.entry.async_create_background_task(
            self.hass, self._async_apply_light(), f"{DOMAIN}_light_{self.entry.entry_id}"
        )

    def _lights_match(self, want_on: bool) -> bool:
        for entity_id in self.light_switches:
            state = self.hass.states.get(entity_id)
            if state is None or state.state not in (STATE_ON, STATE_OFF):
                return False
            if (state.state == STATE_ON) != want_on:
                return False
        return True

    async def _async_apply_light(self) -> None:
        """Switch the lights to the wanted state and verify, retrying on failure."""
        want_on = self.is_day
        for attempt in range(LIGHT_TRIES):
            if attempt == LIGHT_TRIES_BEFORE_PAUSE:
                await asyncio.sleep(LIGHT_RETRY_PAUSE)
            if self._lights_match(want_on):
                break
            await self.hass.services.async_call(
                "homeassistant",
                "turn_on" if want_on else "turn_off",
                {"entity_id": self.light_switches},
                blocking=False,
            )
            await asyncio.sleep(LIGHT_RETRY_DELAY)
        self._set_light_fault(not self._lights_match(want_on))

    @callback
    def _set_light_fault(self, fault: bool) -> None:
        if fault == self.light_fault:
            return
        self.light_fault = fault
        async_dispatcher_send(self.hass, self.signal)
        self._fire_event("light_fault" if fault else "light_fault_cleared")

    @callback
    def _changed(self) -> None:
        self._last_due = self.feeding_due
        self._last_day = self.is_day
        self._store.async_delay_save(self._data_to_save, 1)
        async_dispatcher_send(self.hass, self.signal)

    @callback
    def _handle_source_change(self, event: Event[EventStateChangedData]) -> None:
        async_dispatcher_send(self.hass, self.signal)

    @callback
    def _handle_misting_change(self, event: Event[EventStateChangedData]) -> None:
        """Stamp "last misted" when the misting switch turns on."""
        old, new = event.data["old_state"], event.data["new_state"]
        # Only a real off -> on switch counts, not startup / reconnect noise.
        if old is not None and old.state == STATE_OFF and new and new.state == STATE_ON:
            self.async_set_event("last_misted", dt_util.utcnow())

    @callback
    def _handle_tick(self, now: datetime) -> None:
        due, day = self.feeding_due, self.is_day
        if due != self._last_due or day != self._last_day:
            phase_changed = day != self._last_day
            self._last_due, self._last_day = due, day
            async_dispatcher_send(self.hass, self.signal)
            if phase_changed:
                self._schedule_light_sync()

    def _data_to_save(self) -> dict[str, Any]:
        return {
            "species": self.species_id,
            "setpoints": self.setpoints,
            "light_times": {k: v.isoformat() for k, v in self.light_times.items()},
            "light_automation": self.light_automation,
            "events": {
                k: (v.isoformat() if v else None) for k, v in self.events.items()
            },
        }


type TerrariumConfigEntry = ConfigEntry[TerrariumController]
