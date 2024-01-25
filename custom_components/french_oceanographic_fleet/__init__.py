"""The French Oceanographic Fleet integration."""
from __future__ import annotations

from datetime import UTC, datetime
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import FrenchOceanographicFleetUpdateCoordinator

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.DEVICE_TRACKER]

_LOGGER = logging.getLogger(__name__)


class FleetApi:
    """Fleet API."""

    def __init__(self, ship: str, session: aiohttp.ClientSession, logger) -> None:
        """Initialize."""
        self.ship = ship
        self._session = session
        self._data = []
        self._logger = logger

    async def async_get_data(self):
        """Test if we can get ship information."""
        url = self.get_url()
        self._logger.info("Get url: %s", url)
        response = await self._session.get(url, raise_for_status=True)
        self._data = await response.json()

    def get_url(self) -> str:
        """Generate current URL."""
        return f"https://localisation.flotteoceanographique.fr/api/positions?name={self.ship}&date={datetime.now(tz=UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}"

    @property
    def ship_data(self) -> list:
        """Get ship data."""
        return self._data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up French Oceanographic Fleet from a config entry."""

    session = async_get_clientsession(hass)
    api = FleetApi(
        ship=entry.data["ship"],
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
