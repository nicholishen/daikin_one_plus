import asyncio
import aiohttp
from homeassistant import config_entries, core
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_API_KEY,
    CONF_INTEGRATOR_TOKEN,
    CONF_LOCATION_NAME
)

from .daikin_api import DaikinOnePlusClient

PLATFORMS = ["climate"]

async def async_setup(hass: core.HomeAssistant, config: dict):
    """Set up the Daikin OnePlus integration."""
    return True

async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Set up Daikin OnePlus from a config entry."""
    session = async_get_clientsession(hass)
    client = DaikinOnePlusClient(session,
                                 entry.data[CONF_EMAIL],
                                 entry.data[CONF_API_KEY],
                                 entry.data[CONF_INTEGRATOR_TOKEN],
                                 entry.data.get(CONF_LOCATION_NAME))

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok