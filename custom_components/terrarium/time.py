"""Daily light schedule (light on / light off); defines day and night."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import LIGHT_TIME_KEYS
from .controller import TerrariumConfigEntry, TerrariumController
from .entity import TerrariumEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    async_add_entities(LightTime(controller, key) for key in LIGHT_TIME_KEYS)


class LightTime(TerrariumEntity, TimeEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, controller: TerrariumController, key: str) -> None:
        super().__init__(controller, key)
        self._attr_translation_key = key

    @property
    def native_value(self) -> time:
        return self.controller.light_times[self._key]

    async def async_set_value(self, value: time) -> None:
        self.controller.async_set_light_time(self._key, value)
