"""Binary sensors: out of range, feeding due."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .controller import TerrariumConfigEntry
from .entity import TerrariumEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    async_add_entities(
        [OutOfRange(controller, "out_of_range"), FeedingDue(controller, "feeding_due")]
    )


class OutOfRange(TerrariumEntity, BinarySensorEntity):
    _attr_translation_key = "out_of_range"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        return bool(self.controller.problems)


class FeedingDue(TerrariumEntity, BinarySensorEntity):
    _attr_translation_key = "feeding_due"

    @property
    def is_on(self) -> bool:
        return self.controller.feeding_due
