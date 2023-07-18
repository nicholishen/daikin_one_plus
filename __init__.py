import asyncio
import aiohttp
import logging
from datetime import timedelta
from homeassistant import config_entries, core
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .daikin_api import DaikinOnePlusClient, ServerNotReachable, InvalidCredentials

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_API_KEY,
    CONF_INTEGRATOR_TOKEN,
    CONF_LOCATION_NAME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["climate"]

async def async_setup(hass: core.HomeAssistant, config: dict):
    """Set up the Daikin OnePlus integration."""
    return True

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
):
    """Set up Daikin OnePlus from a config entry."""
    session = async_get_clientsession(hass)
    client = DaikinOnePlusClient(
        session,
        entry.data[CONF_EMAIL],
        entry.data[CONF_API_KEY],
        entry.data[CONF_INTEGRATOR_TOKEN],
        entry.data.get(CONF_LOCATION_NAME),
    )

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            return await client.get_devices_info()
        except InvalidCredentials as ic:
            _LOGGER.error(f"Could not update data due to an error: {ic}. Check the credentials.")
            raise UpdateFailed(f"Invalid credentials provided")
        except ServerNotReachable as snr:
            _LOGGER.error(f"Could not update data due to an error: {snr}. Check the server status.")
            raise UpdateFailed(f"Could not reach the server")
        except Exception as err:
            _LOGGER.error(f"Could not update data due to unknown error: {err}")
            raise UpdateFailed(f"Unknown error occured: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Daikin OnePlus Thermostat",
        update_method=async_update_data,
        update_interval=timedelta(minutes=3),
    )

    await coordinator.async_config_entry_first_refresh()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = {"client": client, "coordinator": coordinator}

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
):
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
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok