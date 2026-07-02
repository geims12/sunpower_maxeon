"""Config flow for SunPower Maxeon."""
from collections.abc import Mapping
from typing import Any
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    TimeSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import DOMAIN
from .api import AsyncConfigEntryAuth

_LOGGER = logging.getLogger(__name__)

class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle SunPower Maxeon OAuth2 authentication."""

    DOMAIN = DOMAIN
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @property
    def extra_authorize_data(self) -> dict[str, str]:
        """Extra data that needs to be appended to the authorize url."""
        return {"scope": "offline_access system.read system.write"}

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create an oauth config entry or update existing entry for reauth."""
        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return await super().async_oauth_create_entry(data)

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle a flow start."""
        await self.async_set_unique_id(DOMAIN)

        if self.source != config_entries.SOURCE_REAUTH and self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await super().async_step_user(user_input)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SunPower Maxeon."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        super().__init__()
        self._entry = config_entry

    async def _get_api(self) -> AsyncConfigEntryAuth:
        websession = async_get_clientsession(self.hass)
        implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(
            self.hass, self._entry
        )
        oauth_session = config_entry_oauth2_flow.OAuth2Session(
            self.hass, self._entry, implementation
        )
        return AsyncConfigEntryAuth(websession, oauth_session)

    async def _get_system_sn(self, api: AsyncConfigEntryAuth) -> str:
        systems = await api.async_get_systems()
        if not systems.get("systems"):
            raise ValueError("No systems returned from API")

        system_sn = systems["systems"][0].get("system_sn")
        if not system_sn:
            raise ValueError("System SN missing in API response")

        return system_sn

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Show the menu with configuration sections."""
        return await self.async_step_menu()

    async def async_step_menu(self, user_input: dict[str, Any] | None = None):
        """Menu step to choose what to configure."""
        return self.async_show_menu(
            step_id="menu",
            menu_options={"charging", "discharging", "export", "ups"},
        )

    async def async_step_charging(self, user_input: dict[str, Any] | None = None):
        """Configure charging schedule."""
        api = await self._get_api()
        system_sn = await self._get_system_sn(api)
        charging = await api.async_get_charging_schedule(system_sn)

        if user_input is not None:
            await api.async_set_charging_schedule(system_sn, {
                "enable": user_input["enable"],
                "start_time_1": user_input["start_time_1"],
                "end_time_1": user_input["end_time_1"],
                "start_time_2": user_input["start_time_2"],
                "end_time_2": user_input["end_time_2"],
                "max_soc": user_input["max_soc"],
            })
            return self.async_create_entry(title="Charging Schedule", data={})

        return self.async_show_form(
            step_id="charging",
            data_schema=vol.Schema({
                vol.Required("enable", default=charging.get("enable", True)): BooleanSelector(),
                vol.Required("start_time_1", default=charging.get("start_time_1", "14:00")): TimeSelector(),
                vol.Required("end_time_1", default=charging.get("end_time_1", "16:00")): TimeSelector(),
                vol.Required("start_time_2", default=charging.get("start_time_2", "20:00")): TimeSelector(),
                vol.Required("end_time_2", default=charging.get("end_time_2", "22:00")): TimeSelector(),
                vol.Required("max_soc", default=charging.get("max_soc", 95)): NumberSelector(
                    NumberSelectorConfig(min=0, max=100, step=1, mode="box", unit_of_measurement="%")
                ),
            }),
        )

    async def async_step_discharging(self, user_input: dict[str, Any] | None = None):
        """Configure discharging schedule."""
        api = await self._get_api()
        system_sn = await self._get_system_sn(api)
        discharging = await api.async_get_discharging_schedule(system_sn)

        if user_input is not None:
            await api.async_set_discharging_schedule(system_sn, {
                "enable": user_input["enable"],
                "start_time_1": user_input["start_time_1"],
                "end_time_1": user_input["end_time_1"],
                "start_time_2": user_input["start_time_2"],
                "end_time_2": user_input["end_time_2"],
                "min_soc": user_input["min_soc"],
            })
            return self.async_create_entry(title="Discharging Schedule", data={})

        return self.async_show_form(
            step_id="discharging",
            data_schema=vol.Schema({
                vol.Required("enable", default=discharging.get("enable", True)): BooleanSelector(),
                vol.Required("start_time_1", default=discharging.get("start_time_1", "14:00")): TimeSelector(),
                vol.Required("end_time_1", default=discharging.get("end_time_1", "16:00")): TimeSelector(),
                vol.Required("start_time_2", default=discharging.get("start_time_2", "20:00")): TimeSelector(),
                vol.Required("end_time_2", default=discharging.get("end_time_2", "22:00")): TimeSelector(),
                vol.Required("min_soc", default=discharging.get("min_soc", 20)): NumberSelector(
                    NumberSelectorConfig(min=0, max=100, step=1, mode="box", unit_of_measurement="%")
                ),
            }),
        )

    async def async_step_export(self, user_input: dict[str, Any] | None = None):
        """Configure export limit."""
        api = await self._get_api()
        system_sn = await self._get_system_sn(api)
        export = await api.async_get_export_limit(system_sn)

        if user_input is not None:
            await api.async_set_export_limit(system_sn, int(user_input["export_rate"]))
            return self.async_create_entry(title="Export Limit", data={})

        return self.async_show_form(
            step_id="export",
            data_schema=vol.Schema({
                vol.Required("export_rate", default=export.get("export_rate", 80)): NumberSelector(
                    NumberSelectorConfig(min=0, max=100, step=1, mode="box", unit_of_measurement="%")
                ),
            }),
        )

    async def async_step_ups(self, user_input: dict[str, Any] | None = None):
        """Configure UPS state."""
        api = await self._get_api()
        system_sn = await self._get_system_sn(api)
        ups = await api.get_battery_ups_state(system_sn)

        if user_input is not None:
            await api.set_battery_ups_state(system_sn, {
                "enable": user_input["enable"]
            })
            return self.async_create_entry(title="UPS State", data={})

        return self.async_show_form(
            step_id="ups",
            data_schema=vol.Schema({
                vol.Required("enable", default=ups.get("enable", True)): BooleanSelector()
            }),
        )