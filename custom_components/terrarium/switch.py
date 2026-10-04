"""Switches: automation toggles."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    if controller.light_switches:
        entities.append(LightAutomation(controller, "light_automation"))
    async_add_entities(entities)


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
