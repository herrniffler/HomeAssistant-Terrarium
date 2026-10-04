"""Sensors: overall status and next feeding."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUS_OPTIONS
from .controller import TerrariumConfigEntry, TerrariumController
from .entity import TerrariumEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    entities: list[TerrariumEntity] = [
        StatusSensor(controller, "status"),
        NextFeedingSensor(controller, "next_feeding"),
    ]
    if controller.temperature_sensors:
        entities.append(
            ReadingSensor(
                controller,
                "temperature",
                controller.temperature_sensors,
                SensorDeviceClass.TEMPERATURE,
                UnitOfTemperature.CELSIUS,
            )
        )
    if controller.humidity_sensors:
        entities.append(
            ReadingSensor(
                controller,
                "humidity",
                controller.humidity_sensors,
                SensorDeviceClass.HUMIDITY,
                PERCENTAGE,
            )
        )
    async_add_entities(entities)


class ReadingSensor(TerrariumEntity, SensorEntity):
    """Current value of the configured source sensors (mean; min/max as attributes)."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        controller: TerrariumController,
        key: str,
        sources: list[str],
        device_class: SensorDeviceClass,
        unit: str,
    ) -> None:
        super().__init__(controller, key)
        self._attr_translation_key = key
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._sources = sources

    @property
    def native_value(self) -> float | None:
        summary = self.controller.reading_summary(self._sources)
        return summary["mean"] if summary else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        summary = self.controller.reading_summary(self._sources)
        return {
            "min": summary["min"] if summary else None,
            "max": summary["max"] if summary else None,
            "sources": self._sources,
        }


class StatusSensor(TerrariumEntity, SensorEntity):
    _attr_translation_key = "status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUS_OPTIONS

    @property
    def native_value(self) -> str:
        return self.controller.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "problems": self.controller.problems,
            "species": self.controller.profile.get("name"),
        }


class NextFeedingSensor(TerrariumEntity, SensorEntity):
    _attr_translation_key = "next_feeding"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        return self.controller.next_feeding
