from __future__ import annotations

import logging
from datetime import datetime

import aiohttp
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import DayOrder, KitafinoClient, KitafinoError
from .const import DOMAIN, SCAN_INTERVAL


class KitafinoCoordinator(DataUpdateCoordinator[dict[str, DayOrder]]):
    def __init__(self, hass, client: KitafinoClient) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.last_successful_update: datetime | None = None

    async def _async_update_data(self) -> dict[str, DayOrder]:
        try:
            orders = await self.client.async_get_orders()
        except (aiohttp.ClientError, TimeoutError, KitafinoError) as err:
            raise UpdateFailed("Kitafino-Daten konnten nicht abgerufen werden.") from err
        self.last_successful_update = dt_util.utcnow()
        return orders