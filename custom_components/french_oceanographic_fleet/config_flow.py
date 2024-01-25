"""Config flow for French Oceanographic Fleet integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SHIP_ID, CONF_SHIP_NAME, DOMAIN, SHIP_ID, SHIP_NAME
from .fleet_api import FleetApi

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SHIP): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    print(data)
    try:
        ship_id = SHIP_ID[data[CONF_SHIP_NAME]]
    except KeyError:
        raise ShipNotFound

    session = async_get_clientsession(hass)

    ship = FleetApi(
        ship_id=ship_id,
        session=session,
        logger=_LOGGER,
    )

    await ship.async_get_data()

    _LOGGER.info("Ship data contains %i items", len(ship.ship_data))

    if not ship.ship_data:
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": SHIP_NAME[ship_id], CONF_SHIP_ID: ship_id}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for French Oceanographic Fleet."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            ship_id = SHIP_ID[user_input[CONF_SHIP_NAME]]
            await self.async_set_unique_id(f"{ship_id}")
            self._abort_if_unique_id_configured()
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except ShipNotFound:
                errors["base"] = "invalid_ship"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data={CONF_SHIP_ID: ship_id})

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class ShipNotFound(HomeAssistantError):
    """Ship name is invalid."""
