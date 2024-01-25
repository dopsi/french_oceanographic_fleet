"""DataUpdateCoordinator for the french_oceanographic_fleet integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import TypedDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from . import FleetApi

_LOGGER = logging.getLogger(__name__)


class FleetDataPoint(TypedDict):
    """Data for a fleet position."""

    id: int
    nav_id: str
    lat: float
    lon: float
    date: datetime
    vit_vent: float
    dir_vent: float
    temp_mer: float
    temp_air: float
    prof_eau: float
    pres_atmo: float


class FrenchOceanographicFleetUpdateCoordinator(DataUpdateCoordinator[FleetDataPoint]):
    """French Oceanographic Fleet Update Coordinator."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: FleetApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=90),
        )

        self._api = api

    async def _async_update_data(self) -> FleetDataPoint:
        await self._api.async_get_data()

        last_datapoint = self._api.ship_data[-1]

        return FleetDataPoint(
            id=last_datapoint["pos_ID"],
            nav_id=last_datapoint["pos_NAV_ID"],
            lat=last_datapoint["pos_LAT"],
            lon=last_datapoint["pos_LONG"],
            date=datetime.strptime(
                last_datapoint["pos_DATE"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ),
            vit_vent=last_datapoint["pos_VITVENT"],
            dir_vent=last_datapoint["pos_DIRVENT"],
            temp_mer=last_datapoint["pos_TEMPMER"],
            temp_air=last_datapoint["pos_TEMPAIR"],
            prof_eau=last_datapoint["pos_PROFEAU"],
            pres_atmo=last_datapoint["pos_PRESATMO"],
        )
