"""Editable target values."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .controller import TerrariumConfigEntry, TerrariumController
from .entity import TerrariumEntity

_TEMP = {
    "device_class": NumberDeviceClass.TEMPERATURE,
    "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
    "native_min_value": 0,
    "native_max_value": 50,
    "native_step": 0.5,
}
_HUM = {
    "device_class": NumberDeviceClass.HUMIDITY,
    "native_unit_of_measurement": PERCENTAGE,
    "native_min_value": 0,
    "native_max_value": 100,
    "native_step": 1,
}

DESCRIPTIONS = (
    NumberEntityDescription(
        key="temp_min", translation_key="temp_min",
        entity_category=EntityCategory.CONFIG, **_TEMP,
    ),
    NumberEntityDescription(
        key="temp_max", translation_key="temp_max",
        entity_category=EntityCategory.CONFIG, **_TEMP,
    ),
    NumberEntityDescription(
        key="humidity_min", translation_key="humidity_min",
        entity_category=EntityCategory.CONFIG, **_HUM,
    ),
    NumberEntityDescription(
        key="humidity_max", translation_key="humidity_max",
        entity_category=EntityCategory.CONFIG, **_HUM,
    ),
    NumberEntityDescription(
        key="feeding_interval", translation_key="feeding_interval",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        native_min_value=0, native_max_value=60, native_step=0.5,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    async_add_entities(SetpointNumber(controller, d) for d in DESCRIPTIONS)


class SetpointNumber(TerrariumEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(
        self, controller: TerrariumController, description: NumberEntityDescription
    ) -> None:
        super().__init__(controller, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        return self.controller.setpoints[self._key]

    async def async_set_native_value(self, value: float) -> None:
        self.controller.async_set_setpoint(self._key, value)
