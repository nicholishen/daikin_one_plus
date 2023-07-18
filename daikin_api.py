import asyncio
import aiohttp
import async_timeout
import json
import logging
import datetime

from aiohttp.client_exceptions import ClientError

from .const import (
    API_BASE_URL,
    API_TOKEN_URL,
    API_DEVICES_URL,
    API_DEVICE_UPDATE_MODE_SETPOINT_URL,
    API_DEVICE_UPDATE_SCHEDULE_URL,
    API_DEVICE_UPDATE_FAN_SETTINGS_URL,
    API_DEVICE_INFO_URL,
)

_LOGGER = logging.getLogger(__name__)


class InvalidTokenResponse(Exception):
    def __init__(self, detail):
        self.message = f"The token endpoint response is not valid: {detail}"
        super().__init__()


class InvalidCredentials(Exception):
    """Raised when the provided credentials are incorrect."""

    pass


class ServerNotReachable(Exception):
    """Raised when unable to reach the server."""

    pass


class DaikinOnePlusClient:
    def __init__(self, session, email, api_key, integrator_token, location_name=None):
        self.session = session
        self.email = email
        self.api_key = api_key
        self.integrator_token = integrator_token
        self.location_name = location_name.lower() if location_name else None
        self.headers = {"Content-Type": "application/json", "x-api-key": self.api_key}
        self.access_token = None
        self.token_expiration = None

    async def _ensure_token_exists(self):
        if (
            self.access_token is None
            or self.token_expiration is None
            or datetime.datetime.now() >= self.token_expiration
        ):
            await self.get_token()

    async def _request(self, method, endpoint, data=None):
        await self._ensure_token_exists()
        url = API_BASE_URL + endpoint
        async with async_timeout.timeout(10):
            async with self.session.request(
                method, url, headers=self.headers, json=data
            ) as response:
                response.raise_for_status()
                return await response.json() if response.content_length > 0 else {}

    async def get_token(self):
        try:
            response = await self._request(
                "POST",
                API_TOKEN_URL,
                data={"email": self.email, "integratorToken": self.integrator_token},
            )
        except ClientError as err:
            raise ServerNotReachable(f"Unable to reach the token endpoint: {err}")
        except Exception as ex:
            raise ex

        if "accessToken" not in response or "accessTokenExpiresIn" not in response:
            raise InvalidCredentials("Invalid email or integrator token provided.")

        self.access_token = response["accessToken"]
        self.headers["Authorization"] = f"Bearer {self.access_token}"
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(
            seconds=response["accessTokenExpiresIn"]
        )

    async def get_devices(self):
        locations_devices = await self._request("GET", API_DEVICES_URL)
        if locations_devices:
            if not self.location_name:
                return locations_devices[0]["devices"]
            for location_devices in locations_devices:
                if (
                    self.location_name.casefold()
                    == location_devices["locationName"].casefold()
                ):
                    return location_devices["devices"]
        return []

    async def get_device_info(self, device_id):
        return await self._request("GET", API_DEVICE_INFO_URL.format(device_id))

    async def update_device_mode_setpoint(
        self, device_id, mode, heat_setpoint, cool_setpoint
    ):
        return await self._request(
            "PUT",
            API_DEVICE_UPDATE_MODE_SETPOINT_URL.format(device_id),
            data={
                "mode": mode,
                "heatSetpoint": heat_setpoint,
                "coolSetpoint": cool_setpoint,
            },
        )

    async def update_device_schedule(self, device_id, schedule_enabled):
        return await self._request(
            "PUT",
            API_DEVICE_UPDATE_SCHEDULE_URL.format(device_id),
            data={"scheduleEnabled": schedule_enabled},
        )

    async def update_device_fan_settings(
        self, device_id, fan_circulate, fan_circulate_speed
    ):
        return await self._request(
            "PUT",
            API_DEVICE_UPDATE_FAN_SETTINGS_URL.format(device_id),
            data={
                "fanCirculate": fan_circulate,
                "fanCirculateSpeed": fan_circulate_speed,
            },
        )

    async def get_devices_info(self):
        devices = await self.get_devices()
        return {
            device["id"]: await self.get_device_info(device["id"]) for device in devices
        }
