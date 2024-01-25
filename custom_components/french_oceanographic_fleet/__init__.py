"""The French Oceanographic Fleet integration."""
from __future__ import annotations

from datetime import UTC, datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SHIP_ID, DOMAIN
from .coordinator import FrenchOceanographicFleetUpdateCoordinator
from .fleet_api import FleetApi

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.DEVICE_TRACKER]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up French Oceanographic Fleet from a config entry."""

    session = async_get_clientsession(hass)
    api = FleetApi(
        ship_id=entry.data[CONF_SHIP_ID],
        session=session,
        logger=_LOGGER,
    )

    coordinator = FrenchOceanographicFleetUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
