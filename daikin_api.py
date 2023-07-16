import asyncio
import aiohttp
import async_timeout
import json
import logging
import datetime

from .const import (
    CONF_API_KEY,
    CONF_EMAIL,
    CONF_INTEGRATOR_TOKEN,
    CONF_LOCATION_NAME
)

_BASE_URL = "https://integrator-api.daikinskyport.com"

class DaikinOnePlusClient:
    def __init__(self, session, email, api_key, integrator_token, location_name=None):
        self.session = session
        self.email = email
        self.api_key = api_key
        self.integrator_token = integrator_token
        self.location_name = location_name.lower() if location_name else None
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        asyncio.create_task(self.get_token())

    async def get_token(self):
        data = {"email": self.email, "integratorToken": self.integrator_token}
        async with self.session.post(f"{_BASE_URL}/v1/token", headers=self.headers, json=data) as resp:
            result = await resp.json()
            
            # Check that 'accessToken' and 'accessTokenExpiresIn' are in the response
            if not 'accessToken' in result or not 'accessTokenExpiresIn' in result:
                raise Exception("Missing accessToken or accessTokenExpiresIn in the response.")
                
            self.access_token = result['accessToken']
            self.headers['Authorization'] = f"Bearer {self.access_token}"
            self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=result['accessTokenExpiresIn'])

    async def _request(self, method, endpoint, data=None):
        url = _BASE_URL + endpoint

        if datetime.datetime.now() >= self.token_expiration:
            await self.get_token()

        async with async_timeout.timeout(10):
            async with self.session.request(method, url, headers=self.headers, json=data) as response:
                response.raise_for_status()
                if response.content_length is not None and response.content_length > 0:
                    return await response.json()
                else:
                    return {}

    async def get_devices(self):
        devices = await self._request("GET", "/v1/devices")
        locations_map = {location['locationName'].lower(): location for location in devices}
        if self.location_name:
            if self.location_name in locations_map:
                return locations_map[self.location_name]['devices']
            else:
                raise ValueError(f"No location found with the name: {self.location_name}")
        else:
            return devices[0]['devices']

    async def get_device_info(self, device_id):
        return await self._request("GET", f"/v1/devices/{device_id}")

    async def update_device_mode_setpoint(self, device_id, mode, heat_setpoint, cool_setpoint):
        data = {'mode': mode, 'heatSetpoint': heat_setpoint, 'coolSetpoint': cool_setpoint}
        return await self._request("PUT", f"/v1/devices/{device_id}/msp", json=data)

    async def update_device_schedule(self, device_id, schedule_enabled):
        return await self._request("PUT", f"/v1/devices/{device_id}/schedule", json={"scheduleEnabled": schedule_enabled})

    async def update_device_fan_settings(self, device_id, fan_circulate, fan_circulate_speed):
        data = {'fanCirculate': fan_circulate, 'fanCirculateSpeed': fan_circulate_speed}
        return await self._request("PUT", f"/v1/devices/{device_id}/fan", json=data)