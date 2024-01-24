"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SHIP_NAME
from .coordinator import FrenchOceanographicFleetUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=90)


def str2lonlat(data: str) -> float:
    """Convert a string to a longitude or latitude."""
    globe_side, deg, minutes = data.split(" ")

    # print(globe_side, deg, minutes)

    globe_side_coef = 1
    if globe_side in ["S", "W"]:
        globe_side_coef = -1

    assert deg[-1] == "°"

    deg_val = int(deg[0:-1])

    min_val = float(minutes) / 60

    return globe_side_coef * (deg_val + min_val)


class FleetShipEntity(
    CoordinatorEntity[FrenchOceanographicFleetUpdateCoordinator], TrackerEntity
):
    """Ship entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_icon = "mdi:ferry"

    def __init__(
        self,
        coordinator: FrenchOceanographicFleetUpdateCoordinator,
        unique_id: str,
        ship_name: str,
    ) -> None:
        """Create device."""
        super().__init__(coordinator=coordinator)
        self._attr_unique_id = f"{unique_id}_ship"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="flotteoceanographique.fr",
            entry_type=DeviceEntryType.SERVICE,
            name=ship_name,
        )

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return str2lonlat(self.coordinator.data["lat"])

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return str2lonlat(self.coordinator.data["lon"])

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Configure a dispatcher connection based on a config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.unique_id
    async_add_entities(
        [
            FleetShipEntity(
                coordinator, unique_id, ship_name=SHIP_NAME[entry.data["ship"]]
            )
        ]
    )
