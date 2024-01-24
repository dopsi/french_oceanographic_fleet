"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FrenchOceanographicFleetUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=90)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
    }
)


class FleetSensor(
    CoordinatorEntity[FrenchOceanographicFleetUpdateCoordinator], SensorEntity
):
    """Fleet sensor."""

    _attr_attribution = "Data provided by localisation.flotteoceanographique.fr"
    _attr_has_entity_name = True
    _fleet_data_key: str

    def __init__(
        self,
        coordinator: FrenchOceanographicFleetUpdateCoordinator,
        unique_id: str,
    ) -> None:
        """Create a sensor."""
        super().__init__(coordinator=coordinator)
        _LOGGER.info("Create fleet sensor")
        self._attr_unique_id = f"{unique_id}_{self._fleet_data_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="flotteoceanographique.fr",
            entry_type=DeviceEntryType.SERVICE
        )

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        return self.coordinator.data[self._fleet_data_key]


class FleetSensorDate(FleetSensor):
    """Fleet date sensor."""

    _attr_icon = "mdi:clock"
    _attr_translation_key = "last_update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _fleet_data_key = "date"


class FleetSensorWaterTemp(FleetSensor):
    """Fleet water temperature sensor."""

    _attr_icon = "mdi:thermometer"
    _attr_translation_key = "water_temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _fleet_data_key = "temp_mer"


class FleetSensorAirTemp(FleetSensor):
    """Fleet water temperature sensor."""

    _attr_icon = "mdi:thermometer"
    _attr_translation_key = "air_temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = "°C"
    _fleet_data_key = "temp_air"


class FleetSensorWindSpeed(FleetSensor):
    """Fleet wind speed sensor."""

    _attr_icon = "mdi:speedometer"
    _attr_translation_key = "wind_speed"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = "kn"
    _fleet_data_key = "vit_vent"


class FleetSensorWaterDepth(FleetSensor):
    """Fleet water depth sensor."""

    _attr_icon = "mdi:tape-measure"
    _attr_translation_key = "water_depth"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = "m"
    _fleet_data_key = "prof_eau"


class FleetSensorAirPressure(FleetSensor):
    """Fleet water depth sensor."""

    _attr_icon = "mdi:gauge"
    _attr_translation_key = "air_pressure"
    _attr_device_class = SensorDeviceClass.PRESSURE
    _attr_native_unit_of_measurement = "hPa"
    _fleet_data_key = "pres_atmo"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from a config entry created in the integrations UI."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id

    async_add_entities(
        [
            FleetSensorDate(coordinator, unique_id),
            FleetSensorWaterTemp(coordinator, unique_id),
            FleetSensorAirTemp(coordinator, unique_id),
            FleetSensorWindSpeed(coordinator, unique_id),
            FleetSensorWaterDepth(coordinator, unique_id),
            FleetSensorAirPressure(coordinator, unique_id),
        ],
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    _LOGGER.info("Setup platform")
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_IMPORT},
        data=config,
    )
