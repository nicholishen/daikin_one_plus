import logging, asyncio
from typing import Optional, List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_FAHRENHEIT

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    HVAC_MODE_AUTO_STR,
    HVAC_MODE_OFF_STR,
    HVAC_MODE_HEAT_STR,
    HVAC_MODE_COOL_STR,
    DEVICE_TYPE_THERMOSTAT,
    COOLDOWN_INTERVAL,
    EVENT_DAIKIN_ONEPLUS_HVAC_MODE_CHANGE,
    EVENT_DAIKIN_ONEPLUS_FAN_MODE_CHANGE,
    EVENT_DAIKIN_ONEPLUS_TARGET_TEMP_CHANGE,
    EVENT_DAIKIN_ONEPLUS_SCHEDULE_MODE_CHANGE,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_HVAC_MODES = [HVAC_MODE_AUTO, HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL]


async def async_setup_entry(hass, config_entry, async_add_entities):
    hub = hass.data[DOMAIN][config_entry.entry_id]
    client = hub["client"]

    devices = await client.get_devices()
    thermostat_entities = [
        DaikinOnePlusThermostat(client, device)
        for device in devices
        if device["type"] == DEVICE_TYPE_THERMOSTAT
    ]
    async_add_entities(thermostat_entities, True)


class DaikinOnePlusThermostat(ClimateEntity):
    def __init__(self, client, device_info):
        """Initialize the thermostat."""
        self.client = client
        self.device_info = device_info
        self.device_id = device_info["id"]
        self.device_state = None
        self._attr_name = device_info.get("name", DEFAULT_NAME)
        self._refresh_scheduled = False

    async def _async_schedule_refresh(self):
        """Private method to schedule a refresh."""
        if not self._refresh_scheduled:
            self._refresh_scheduled = True
            await asyncio.sleep(COOLDOWN_INTERVAL)
            self._refresh_scheduled = False
            self.hass.bus.async_request_refresh()

    async def async_update(self):
        """Get the latest data and updates the state."""
        self.device_state = await self.client.get_device_info(self.device_id)
        _LOGGER.debug(f"Update state: {self.device_state}")

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self.device_id

    @property
    def hvac_mode(self):
        """Return the current HVAC mode (auto, off, heat, cool)."""
        mode = self.device_state.get("mode", "").lower()
        if mode == HVAC_MODE_AUTO_STR:
            return HVAC_MODE_AUTO
        elif mode == HVAC_MODE_OFF_STR:
            return HVAC_MODE_OFF
        elif mode == HVAC_MODE_HEAT_STR:
            return HVAC_MODE_HEAT
        elif mode == HVAC_MODE_COOL_STR:
            return HVAC_MODE_COOL
        else:
            return None

    @property
    def hvac_modes(self) -> list:
        """Return the list of available modes."""
        return SUPPORTED_HVAC_MODES

    ...

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target HVAC mode."""
        response = await self.client.update_device_mode_setpoint(
            self.device_id,
            hvac_mode.lower(),
            self.target_temperature,
            self.target_temperature,
        )

        if not 200 <= response.status < 300:
            _LOGGER.error(
                f"Failed to update the HVAC mode to {hvac_mode}, status code {response.status}"
            )
            return

        await self._async_schedule_refresh()
        self.hass.bus.fire(
            EVENT_DAIKIN_ONEPLUS_HVAC_MODE_CHANGE,
            {"device_id": self.device_id, "hvac_mode": hvac_mode},
        )

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            response = await self.client.update_device_mode_setpoint(
                self.device_id, self.hvac_mode, temperature, temperature
            )
            if not 200 <= response.status < 300:
                _LOGGER.error(
                    f"Failed to update the target temperature to {temperature}, status code {response.status}"
                )
                return

            await self._async_schedule_refresh()
            self.hass.bus.fire(
                EVENT_DAIKIN_ONEPLUS_TARGET_TEMP_CHANGE,
                {"device_id": self.device_id, "target_temperature": temperature},
            )

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        is_circulate = fan_mode.lower() == "circulate"
        response = await self.client.update_device_fan_settings(
            self.device_id, is_circulate, 1 if is_circulate else 0
        )
        if not 200 <= response.status < 300:
            _LOGGER.error(
                f"Failed to update the fan mode to {fan_mode}, status code {response.status}"
            )
            return

        await self._async_schedule_refresh()
        self.hass.bus.fire(
            EVENT_DAIKIN_ONEPLUS_FAN_MODE_CHANGE,
            {"device_id": self.device_id, "fan_mode": fan_mode},
        )

    async def async_set_schedule(self, schedule_mode):
        """Set new schedule mode."""
        response = await self.client.update_device_schedule(
            self.device_id, schedule_mode
        )
        if not 200 <= response.status < 300:
            _LOGGER.error(
                f"Failed to update the schedule mode to {schedule_mode}, status code {response.status}"
            )
            return

        await self._async_schedule_refresh()
        self.hass.bus.fire(
            EVENT_DAIKIN_ONEPLUS_SCHEDULE_MODE_CHANGE,
            {"device_id": self.device_id, "schedule_mode": schedule_mode},
        )
