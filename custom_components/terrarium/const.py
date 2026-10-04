"""Constants for the Terrarium integration."""

from __future__ import annotations

DOMAIN = "terrarium"

CONF_SPECIES = "species"
CONF_TEMPERATURE_SENSORS = "temperature_sensors"
CONF_HUMIDITY_SENSORS = "humidity_sensors"
CONF_MISTING_SWITCH = "misting_switch"

SPECIES_CUSTOM = "custom"
USER_SPECIES_FILE = "terrarium_species.json"

STORE_VERSION = 1

# Editable target values (exposed as number entities)
SETPOINT_KEYS = (
    "temp_min",
    "temp_max",
    "humidity_min",
    "humidity_max",
    "feeding_interval",
    # Night values; default to the day values unless the profile sets them
    "temp_min_night",
    "temp_max_night",
    "humidity_min_night",
    "humidity_max_night",
)
GENERIC_DEFAULTS: dict[str, float] = {
    "temp_min": 18.0,
    "temp_max": 32.0,
    "humidity_min": 40.0,
    "humidity_max": 90.0,
    "feeding_interval": 0.0,  # 0 = disabled
}

# Daily light schedule (exposed as time entities); day = on <= now < off
LIGHT_TIME_KEYS = ("light_on", "light_off")
DEFAULT_LIGHT_TIMES = {"light_on": "08:00:00", "light_off": "20:00:00"}

# Logged care events (exposed as datetime entities / buttons)
EVENT_KEYS = ("last_fed", "last_shed", "last_misted")

STATUS_OK = "ok"
STATUS_TOO_HOT = "too_hot"
STATUS_TOO_COLD = "too_cold"
STATUS_TOO_DRY = "too_dry"
STATUS_TOO_HUMID = "too_humid"
STATUS_NO_DATA = "no_data"
STATUS_OPTIONS = [
    STATUS_OK,
    STATUS_TOO_HOT,
    STATUS_TOO_COLD,
    STATUS_TOO_DRY,
    STATUS_TOO_HUMID,
    STATUS_NO_DATA,
]
