"""Care log timestamps (last fed / shed / misted)."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import EVENT_KEYS
from .controller import TerrariumConfigEntry
from .entity import TerrariumEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    async_add_entities(EventDateTime(controller, key) for key in EVENT_KEYS)


class EventDateTime(TerrariumEntity, DateTimeEntity):
    def __init__(self, controller, key: str) -> None:
        super().__init__(controller, key)
        self._attr_translation_key = key

    @property
    def native_value(self) -> datetime | None:
        return self.controller.events[self._key]

    async def async_set_value(self, value: datetime) -> None:
        self.controller.async_set_event(self._key, value)
