"""Species profile loading (bundled + user-defined)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from .const import USER_SPECIES_FILE

_LOGGER = logging.getLogger(__name__)


def _load(user_path: str) -> dict[str, dict[str, Any]]:
    bundled = Path(__file__).parent / "species.json"
    data: dict[str, dict[str, Any]] = json.loads(bundled.read_text(encoding="utf-8"))

    user_file = Path(user_path)
    if user_file.is_file():
        try:
            user = json.loads(user_file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            _LOGGER.warning("Could not read %s: %s", user_file, err)
        else:
            if isinstance(user, dict):
                for key, profile in user.items():
                    if isinstance(profile, dict):
                        data[key] = profile
            else:
                _LOGGER.warning("%s must contain a JSON object", user_file)
    return data


async def async_load_species(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Return all known species profiles (user file overrides bundled)."""
    return await hass.async_add_executor_job(
        _load, hass.config.path(USER_SPECIES_FILE)
    )
