from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_EMAIL, CONF_API_KEY
from .const import CONF_INTEGRATOR_TOKEN, CONF_LOCATION_NAME, DOMAIN

import aiohttp
from aiohttp.client_exceptions import ClientError

import voluptuous as vol

from .daikin_api import DaikinOnePlusClient

class DaikinOnePlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daikin OnePlus."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step via user input."""
        if user_input is None:
            return self._show_setup_form()

        errors = await self._validate_input(user_input)
        if errors is not None:
            return self._show_setup_form(errors)
        
        return self.async_create_entry(
            title="Daikin One+",
            data=user_input
        )

    async def _validate_input(self, user_input):
        """Return error message if user input is invalid."""
        session = aiohttp.client.ClientSession()
        client = DaikinOnePlusClient(session,
                                     user_input[CONF_EMAIL],
                                     user_input[CONF_API_KEY],
                                     user_input[CONF_INTEGRATOR_TOKEN],
                                     user_input[CONF_LOCATION_NAME])
        try:
            await client.get_token()
        except ClientError as exc:
            return {"base": "auth_error"}
        finally:
            await session.close()

        return None

    def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_INTEGRATOR_TOKEN): str,
                vol.Optional(CONF_LOCATION_NAME): str
            }),
            errors=errors or {},
        )