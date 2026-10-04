"""Constants for the Terrarium integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "terrarium"
EVENT_TERRARIUM = f"{DOMAIN}_event"

CONF_SPECIES = "species"
CONF_TEMPERATURE_SENSORS = "temperature_sensors"
CONF_COLD_TEMPERATURE_SENSORS = "cold_temperature_sensors"
CONF_HUMIDITY_SENSORS = "humidity_sensors"
CONF_BOTTOM_HUMIDITY_SENSORS = "bottom_humidity_sensors"
CONF_MISTING_SWITCH = "misting_switch"
CONF_LIGHT_SWITCHES = "light_switches"

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
    # Cooling: lights go off above the threshold (0 = disabled) until it has cooled
    "cooling_threshold",
    "cooling_spread",
    # Automatic misting (needs a misting switch): mist below this humidity (default
    # derived from the day range), for N seconds, at most every N minutes
    "misting_below",
    "misting_duration",
    "misting_interval",
    # Cold side of a gradient (needs cold-side sensors); by day the temp_* values above
    # then apply to the warm side. At night all sensors share the night range.
    "cold_temp_min",
    "cold_temp_max",
    "gradient_min",
)
# Cold-side setpoints start out equal to the warm-side value they mirror
COLD_DEFAULT_FROM = {"cold_temp_min": "temp_min", "cold_temp_max": "temp_max"}
GENERIC_DEFAULTS: dict[str, float] = {
    "gradient_min": 0.0,  # min. warm-cold difference, 0 = not checked
    "misting_duration": 30.0,  # seconds
    "misting_interval": 60.0,  # minutes between two misting runs
    "cooling_threshold": 0.0,  # 0 = disabled
    "cooling_spread": 2.0,  # max. difference warmest/coldest sensor to resume
    "temp_min": 18.0,
    "temp_max": 32.0,
    "humidity_min": 40.0,
    "humidity_max": 90.0,
    "feeding_interval": 0.0,  # 0 = disabled
}

# Daily light schedule (exposed as time entities); day = on <= now < off
LIGHT_TIME_KEYS = ("light_on", "light_off")
DEFAULT_LIGHT_TIMES = {"light_on": "08:00:00", "light_off": "20:00:00"}

# Light switching: 3 tries 5 s apart, pause 12 min, 3 more tries, then report a fault
LIGHT_TRIES = 6
LIGHT_TRIES_BEFORE_PAUSE = 3
LIGHT_RETRY_DELAY = 5  # seconds
LIGHT_RETRY_PAUSE = 12 * 60  # seconds

COOLING_START_DELAY = timedelta(minutes=5)  # must stay hot this long
COOLING_RECOVER_DELAY = timedelta(minutes=10)  # must stay recovered this long
COOLING_TIMEOUT = timedelta(hours=4)

# Setpoints that only make sense with a misting switch
MISTING_KEYS = ("misting_below", "misting_duration", "misting_interval")
# Setpoints that only make sense with cold-side sensors
COLD_SIDE_KEYS = ("cold_temp_min", "cold_temp_max", "gradient_min")

# Logged care events (exposed as datetime entities / buttons)
EVENT_KEYS = ("last_fed", "last_shed", "last_misted")

STATUS_OK = "ok"
STATUS_TOO_HOT = "too_hot"
STATUS_TOO_COLD = "too_cold"
STATUS_TOO_DRY = "too_dry"
STATUS_TOO_HUMID = "too_humid"
STATUS_NO_DATA = "no_data"
STATUS_COLD_SIDE_TOO_HOT = "cold_side_too_hot"
STATUS_COLD_SIDE_TOO_COLD = "cold_side_too_cold"
STATUS_NO_GRADIENT = "no_gradient"
STATUS_OPTIONS = [
    STATUS_OK,
    STATUS_TOO_HOT,
    STATUS_TOO_COLD,
    STATUS_COLD_SIDE_TOO_HOT,
    STATUS_COLD_SIDE_TOO_COLD,
    STATUS_NO_GRADIENT,
    STATUS_TOO_DRY,
    STATUS_TOO_HUMID,
    STATUS_NO_DATA,
]
