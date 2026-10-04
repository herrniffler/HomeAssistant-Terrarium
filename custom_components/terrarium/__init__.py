"""Terrarium: species profiles, target ranges and care log for terrariums."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import CONF_SPECIES, DOMAIN, SPECIES_CUSTOM, STORE_VERSION
from .controller import TerrariumConfigEntry, TerrariumController
from .species import async_load_species

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DATETIME,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: TerrariumConfigEntry) -> bool:
    config = {**entry.data, **entry.options}
    species_id = config.get(CONF_SPECIES, SPECIES_CUSTOM)
    species = await async_load_species(hass)

    controller = TerrariumController(
        hass, entry, species_id, species.get(species_id, {}), config
    )
    await controller.async_load()
    entry.runtime_data = controller
    controller.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TerrariumConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_flush()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: TerrariumConfigEntry) -> None:
    await Store(hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()


async def _async_reload(hass: HomeAssistant, entry: TerrariumConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
