"""Switches: automation toggles."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .controller import TerrariumConfigEntry, TerrariumController
from .entity import TerrariumEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    entities: list[TerrariumEntity] = []
    if controller.misting_switch:
        entities.append(AutoMisting(controller, "auto_misting"))
    if controller.light_switches:
        entities.append(LightControl(controller, "light"))
        entities.append(LightAutomation(controller, "light_automation"))
    async_add_entities(entities)


class AutoMisting(TerrariumEntity, SwitchEntity):
    """When on, the misting switch is run automatically if it is too dry (day only)."""

    _attr_translation_key = "auto_misting"

    @property
    def is_on(self) -> bool:
        return self.controller.auto_misting

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.controller.async_set_auto_misting(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.controller.async_set_auto_misting(False)


class LightControl(TerrariumEntity, SwitchEntity):
    """Shows whether the configured lights are on and switches them all together.

    It does not touch the light automation: the lights stay as set until the schedule
    changes the phase again.
    """

    _attr_translation_key = "light"

    def _known_states(self) -> list[str]:
        states = (self.hass.states.get(e) for e in self.controller.light_switches)
        return [
            s.state
            for s in states
            if s is not None and s.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
        ]

    @property
    def available(self) -> bool:
        return bool(self._known_states())

    @property
    def is_on(self) -> bool:
        return all(state == STATE_ON for state in self._known_states())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "switches": {
                entity_id: (
                    state.state
                    if (state := self.hass.states.get(entity_id)) is not None
                    else None
                )
                for entity_id in self.controller.light_switches
            }
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set(False)

    async def _async_set(self, on: bool) -> None:
        await self.hass.services.async_call(
            "homeassistant",
            "turn_on" if on else "turn_off",
            {"entity_id": self.controller.light_switches},
            blocking=False,
        )


class LightAutomation(TerrariumEntity, SwitchEntity):
    """When on, the configured lights follow the light-on / light-off times."""

    _attr_translation_key = "light_automation"

    def __init__(self, controller: TerrariumController, key: str) -> None:
        super().__init__(controller, key)

    @property
    def is_on(self) -> bool:
        return self.controller.light_automation

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.controller.async_set_light_automation(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.controller.async_set_light_automation(False)
