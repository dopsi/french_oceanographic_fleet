"""Fleet script."""

from datetime import UTC, datetime

import aiohttp

from .const import SHIP_ID


class FleetApi:
    """Fleet API."""

    def __init__(self, ship_id: str, session: aiohttp.ClientSession, logger) -> None:
        """Initialize."""
        self.ship_id = ship_id
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
        return f"https://localisation.flotteoceanographique.fr/api/positions?name={self.ship_id}&date={datetime.now(tz=UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}"

    @property
    def ship_data(self) -> list:
        """Get ship data."""
        return self._data