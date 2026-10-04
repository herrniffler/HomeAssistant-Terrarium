"""One-tap buttons that stamp the care log with the current time."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .controller import TerrariumConfigEntry
from .entity import TerrariumEntity

# button key -> care event it stamps
BUTTONS = {"fed": "last_fed", "shed": "last_shed", "misted": "last_misted"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TerrariumConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller = entry.runtime_data
    async_add_entities(CareButton(controller, key, ev) for key, ev in BUTTONS.items())


class CareButton(TerrariumEntity, ButtonEntity):
    def __init__(self, controller, key: str, event_key: str) -> None:
        super().__init__(controller, f"btn_{key}")
        self._attr_translation_key = key
        self._event_key = event_key

    async def async_press(self) -> None:
        self.controller.async_set_event(self._event_key, dt_util.utcnow())
