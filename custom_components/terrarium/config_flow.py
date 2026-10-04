"""Config and options flow for Terrarium."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)
from homeassistant.util import slugify

from .const import (
    CONF_COLD_TEMPERATURE_SENSORS,
    CONF_HUMIDITY_SENSORS,
    CONF_LIGHT_SWITCHES,
    CONF_MISTING_SWITCH,
    CONF_SPECIES,
    CONF_TEMPERATURE_SENSORS,
    DOMAIN,
    SPECIES_CUSTOM,
)
from .species import async_load_species


def _sensor_fields(species: dict[str, dict[str, Any]]) -> dict[Any, Any]:
    options = [
        SelectOptionDict(
            value=key,
            label=f"{p['name']} ({p['common']})" if p.get("common") else p["name"],
        )
        for key, p in sorted(species.items(), key=lambda kv: kv[1].get("name", kv[0]))
    ]
    options.append(SelectOptionDict(value=SPECIES_CUSTOM, label="Custom / Eigenes Profil"))
    return {
        vol.Required(CONF_SPECIES, default=SPECIES_CUSTOM): SelectSelector(
            SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
        ),
        vol.Optional(CONF_TEMPERATURE_SENSORS, default=[]): EntitySelector(
            EntitySelectorConfig(
                domain=Platform.SENSOR,
                device_class=SensorDeviceClass.TEMPERATURE,
                multiple=True,
            )
        ),
        vol.Optional(CONF_COLD_TEMPERATURE_SENSORS, default=[]): EntitySelector(
            EntitySelectorConfig(
                domain=Platform.SENSOR,
                device_class=SensorDeviceClass.TEMPERATURE,
                multiple=True,
            )
        ),
        vol.Optional(CONF_HUMIDITY_SENSORS, default=[]): EntitySelector(
            EntitySelectorConfig(
                domain=Platform.SENSOR,
                device_class=SensorDeviceClass.HUMIDITY,
                multiple=True,
            )
        ),
        vol.Optional(CONF_MISTING_SWITCH): EntitySelector(
            EntitySelectorConfig(domain=Platform.SWITCH)
        ),
        vol.Optional(CONF_LIGHT_SWITCHES, default=[]): EntitySelector(
            EntitySelectorConfig(domain=[Platform.SWITCH, Platform.LIGHT], multiple=True)
        ),
    }


class TerrariumConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        species = await async_load_species(self.hass)
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            await self.async_set_unique_id(slugify(name))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={CONF_NAME: name},
                options={k: v for k, v in user_input.items() if k != CONF_NAME},
            )
        schema = vol.Schema(
            {vol.Required(CONF_NAME): TextSelector(), **_sensor_fields(species)}
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TerrariumOptionsFlow()


class TerrariumOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        species = await async_load_species(self.hass)
        schema = self.add_suggested_values_to_schema(
            vol.Schema(_sensor_fields(species)), self.config_entry.options
        )
        return self.async_show_form(step_id="init", data_schema=schema)
