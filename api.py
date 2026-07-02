import logging
from aiohttp import ClientSession, ClientResponseError
from homeassistant.helpers import config_entry_oauth2_flow

from .const import SYSTEMS, SYSTEM_DETAILS, POWER_METER, ENERGY_METER, CHARGING_SCHEDULE, DISCHARGING_SCHEDULE, EXPORT_LIMIT

_LOGGER = logging.getLogger(__name__)


class AsyncConfigEntryAuth:
    """Handle authenticated communication with the SunPower Maxeon API."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        self._websession = websession
        self._oauth_session = oauth_session

    async def async_get_access_token(self) -> str:
        """Ensure the OAuth token is valid and return the access token."""
        await self._oauth_session.async_ensure_token_valid()
        return self._oauth_session.token["access_token"]

    async def async_get_systems(self) -> dict:
        """Fetch list of systems from the SunPower Maxeon API."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.sunpowerglobal.com/v1/systems"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received systems: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning("Received 404, returning dummy systems data")
                return {"systems": SYSTEMS.get("systems", [])}
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch systems: %s", err)
            return {"systems": SYSTEMS.get("systems", [])}

    async def async_get_system_details(self, system_sn: str) -> dict:
        """Fetch system details for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received systems data: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"System {system_sn} not found,(HTTP {err.status}), returning dummy data")
                return SYSTEM_DETAILS.get("default", {})
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch system details: %s", err)
            return SYSTEM_DETAILS.get("default", {})

    async def async_get_system_power(self, system_sn: str) -> dict:
        """Fetch system power data from the power meter endpoint."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/power_meter"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received power meter data: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Power data for system {system_sn} not found,(HTTP {err.status}), returning dummy data")
                return POWER_METER
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch system power data: %s", err)
            return POWER_METER

    async def async_get_system_energy(self, system_sn: str) -> dict:
        """Fetch system energy data from the energy meter endpoint."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/energy_meter"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                text = await resp.text()  # Read full response in case of error
                if resp.status != 200:
                    _LOGGER.error("Energy meter request failed: %s - %s", resp.status, text)
                    resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received energy meter: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Energy data for system {system_sn} not found,(HTTP {err.status}), returning dummy data")
                return ENERGY_METER
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch system energy data: %s", err)
            return ENERGY_METER


    async def get_battery_ups_state(self, system_sn: str) -> dict:
        """Fetch the current UPS battery state (enabled/disabled)."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/battery_ups"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received battery ups data: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Battery UPS data for system {system_sn} not found, (HTTP {err.status}), returning dummy data")
                return {"enable": False}
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch battery UPS state: %s", err)
            return {"enable": False}


    async def set_battery_ups_state(self, system_sn: str, enable: bool) -> None:
        """Set the UPS battery enabled state."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"enable": enable}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/battery_ups"

        try:
            async with self._websession.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Cannot update battery UPS state for {system_sn}: not found")
            else:
                raise
        except Exception as err:
            _LOGGER.error("Failed to update battery UPS state: %s", err)

    async def async_get_charging_schedule(self, system_sn: str) -> dict:
        """Fetch the battery charging schedule for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/charging_schedule"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received charghing schedule: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Charging schedule for system {system_sn} not found, (HTTP {err.status}), returning dummy data")
                return CHARGING_SCHEDULE
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch charging schedule: %s", err)
            return CHARGING_SCHEDULE
    
    async def async_set_charging_schedule(self, system_sn: str, schedule: dict) -> None:
        """Set the battery charging schedule for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/charging_schedule"

        try:
            async with self._websession.put(url, headers=headers, json=schedule) as resp:
                resp.raise_for_status()
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Cannot update charging schedule for system {system_sn}: not found(HTTP {err.status}), returning dummy data")
            else:
                raise
        except Exception as err:
            _LOGGER.error("Failed to update charging schedule: %s", err)

    async def async_get_discharging_schedule(self, system_sn: str) -> dict:
        """Fetch the battery discharging schedule for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/discharging_schedule"

        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received discharghing schedule: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Discharging schedule for system {system_sn} not found, (HTTP {err.status}), returning dummy data")
                return DISCHARGING_SCHEDULE
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch discharging schedule: %s", err)
            return DISCHARGING_SCHEDULE
    
    async def async_set_discharging_schedule(self, system_sn: str, schedule: dict) -> None:
        """Set the battery discharging schedule for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/discharging_schedule"

        try:
            async with self._websession.put(url, headers=headers, json=schedule) as resp:
                resp.raise_for_status()
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Cannot update discharging schedule for system {system_sn}: not found(HTTP {err.status})")
            else:
                raise
        except Exception as err:
            _LOGGER.error("Failed to update discharging schedule: %s", err)

    async def async_get_export_limit(self, system_sn: str) -> dict:
        """Fetch the current export limit for the system."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/export_limit"
        try:
            async with self._websession.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.info("Received export limit: %s", data)
                return data
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Export limit for system {system_sn} not found,(HTTP {err.status}), returning dummy data")
                return EXPORT_LIMIT
            raise
        except Exception as err:
            _LOGGER.error("Failed to fetch export limit: %s", err)
            return EXPORT_LIMIT
        
    async def async_set_export_limit(self, system_sn: str, export_rate: int) -> bool:
        """Set a new export limit (in %) for the system."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/export_limit"
        payload = {"export_rate": export_rate}
        try:
            async with self._websession.put(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                return True
        except ClientResponseError as err:
            if err.status in (404, 400):
                _LOGGER.warning(f"Cannot update export limit for system {system_sn}: not found")
            else:
                raise
        except Exception as err:
            _LOGGER.error("Failed to update export limit: %s", err)

    async def async_set_remote_dispatching(self, system_sn: str, payload: dict) -> None:
        """Send a remote dispatching command for a specific system by serial number."""
        token = await self.async_get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://api.sunpowerglobal.com/v1/systems/{system_sn}/remote_dispatching"

        # Unlike the read endpoints (which fall back to dummy data), this is a
        # control action: let failures propagate so the caller can surface them
        # instead of silently reporting success.
        async with self._websession.post(url, headers=headers, json=payload) as resp:
            resp.raise_for_status()