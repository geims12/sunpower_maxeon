from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    DOMAIN,
    REMOTE_DISPATCH_CONTROL_MODES,
    SERVICE_REMOTE_DISPATCH,
    shared_data,
)
from . import api
from .coordinator import SunPowerFullCoordinator, SunPowerRealtimeCoordinator, SunPowerPeriodicCoordinator
from .config_flow import OptionsFlowHandler

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.SENSOR]

type SunPowerConfigEntry = ConfigEntry[SunPowerFullCoordinator]

SERVICE_REMOTE_DISPATCH_SCHEMA = vol.Schema({
    vol.Optional("enable", default=True): BooleanSelector(),
    vol.Required("control_mode"): SelectSelector(
        SelectSelectorConfig(
            options=list(REMOTE_DISPATCH_CONTROL_MODES),
            translation_key="remote_dispatch_control_mode",
        )
    ),
    vol.Optional("duration_minutes", default=10): NumberSelector(
        NumberSelectorConfig(min=2, max=1440, step=1, unit_of_measurement="min")
    ),
    vol.Optional("power", default=0): NumberSelector(
        NumberSelectorConfig(min=0, max=10000, step=50, unit_of_measurement="W")
    ),
    vol.Optional("target_soc", default=0): NumberSelector(
        NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%")
    ),
    vol.Optional("enable_pv", default=False): BooleanSelector(),
})


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Options updated; reloading config entry.")
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_handle_remote_dispatch(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle the remote_dispatch service call."""
    domain_data = hass.data.get(DOMAIN, {})
    if not domain_data:
        raise HomeAssistantError("No SunPower Maxeon integration is configured.")

    entry_data = next(iter(domain_data.values()))
    system_sn = entry_data["shared_data"].get("system_sn")
    if not system_sn:
        raise HomeAssistantError("No SunPower Maxeon system serial number available.")

    mode = call.data["control_mode"]
    control_mode = REMOTE_DISPATCH_CONTROL_MODES[mode]
    power = int(call.data["power"])
    target_soc = int(call.data["target_soc"])

    # The API requires power for modes 1 (pv_only_charge) and 2
    # (forced_charge_discharge), and target_soc for mode 2.
    if mode in ("pv_only_charge", "forced_charge_discharge") and power <= 0:
        raise HomeAssistantError(f"Control mode '{mode}' requires a Power value greater than 0.")
    if mode == "forced_charge_discharge" and target_soc <= 0:
        raise HomeAssistantError(
            f"Control mode '{mode}' requires a Target state of charge greater than 0."
        )

    payload = {
        "enable": call.data["enable"],
        "control_mode": control_mode,
        "duration": int(call.data["duration_minutes"]) * 60,
        "power": power,
        "target_soc": target_soc,
        "enable_pv": call.data["enable_pv"],
    }
    try:
        await entry_data["full"].api.async_set_remote_dispatching(system_sn, payload)
    except Exception as err:
        raise HomeAssistantError(
            f"Failed to submit remote dispatch for system {system_sn}: {err}"
        ) from err

    # Refresh real-time power so the effect of the dispatch shows up promptly.
    await entry_data["realtime"].async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SunPower Maxeon from a config entry."""
    implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(hass, entry)
    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    auth = api.AsyncConfigEntryAuth(
        aiohttp_client.async_get_clientsession(hass), session
    )

    # Create all coordinators
    full_coordinator = SunPowerFullCoordinator(hass, auth, shared_data)
    realtime_coordinator = SunPowerRealtimeCoordinator(hass, auth, shared_data)
    periodic_coordinator = SunPowerPeriodicCoordinator(hass, auth, shared_data)

    try:
        await full_coordinator.async_config_entry_first_refresh()
        await realtime_coordinator.async_config_entry_first_refresh()
        await periodic_coordinator.async_config_entry_first_refresh()

        if not shared_data.get("system_sn"):
            raise ConfigEntryNotReady("No systems found in SunPower account.")

    except Exception as err:
        raise ConfigEntryNotReady(f"Error connecting to SunPower API: {err}") from err

    # Store coordinators in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "full": full_coordinator,
        "realtime": realtime_coordinator,
        "periodic": periodic_coordinator,
        "shared_data": shared_data,
    }

    entry.async_on_unload(entry.add_update_listener(update_listener))

    if not hass.services.has_service(DOMAIN, SERVICE_REMOTE_DISPATCH):
        async def _handle_remote_dispatch(call: ServiceCall) -> None:
            await _async_handle_remote_dispatch(hass, call)

        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOTE_DISPATCH,
            _handle_remote_dispatch,
            schema=SERVICE_REMOTE_DISPATCH_SCHEMA,
        )

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    return True



async def async_unload_entry(hass: HomeAssistant, entry: SunPowerConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_REMOTE_DISPATCH)
    return unload_ok