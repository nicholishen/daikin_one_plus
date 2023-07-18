from aiohttp.client_exceptions import ClientError
import voluptuous as vol
from homeassistant.const import CONF_EMAIL
from .const import (
    CONF_INTEGRATOR_TOKEN,
    CONF_LOCATION_NAME,
    DOMAIN,
    CONF_API_KEY,
    DEFAULT_NAME,
)
from .daikin_api import DaikinOnePlusClient


def validate_email(email_str):
    """Validate that an email string is of the form name@example.com."""
    if "@" in email_str and "." in email_str:
        parts = email_str.split("@")
        if len(parts) == 2:
            domain_parts = parts[1].split(".")
            if len(domain_parts) >= 2:
                return email_str
    raise vol.Invalid("Invalid email address")


class DaikinOnePlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daikin OnePlus."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step via user input."""
        if user_input is None:
            return self._show_setup_form()

        try:
            session = aiohttp.ClientSession()
            client = DaikinOnePlusClient(
                session,
                user_input[CONF_EMAIL],
                user_input[CONF_API_KEY],
                user_input[CONF_INTEGRATOR_TOKEN],
                user_input.get(CONF_LOCATION_NAME),
            )

            await client.get_token()
        except ClientError:
            return self._show_setup_form({"base": "connection_error"})
        except Exception as e:
            return self._show_setup_form({"base": "auth_error"})
        finally:
            await session.close()

        return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

    def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): validate_email,
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_INTEGRATOR_TOKEN): vol.All(
                        str, vol.Length(min=16)
                    ),
                    vol.Optional(CONF_LOCATION_NAME): str,
                }
            ),
            errors=errors or {},
        )
