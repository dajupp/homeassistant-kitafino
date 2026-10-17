from __future__ import annotations

import logging

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import KitafinoClient, KitafinoError
from .const import DOMAIN, SCAN_INTERVAL


class KitafinoCoordinator(DataUpdateCoordinator[dict[str, bool]]):
    def __init__(self, hass, client: KitafinoClient) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, bool]:
        try:
            return await self.client.async_get_orders()
        except (aiohttp.ClientError, TimeoutError, KitafinoError) as err:
            raise UpdateFailed("Kitafino-Daten konnten nicht abgerufen werden.") from err