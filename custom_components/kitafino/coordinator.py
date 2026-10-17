from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import aiohttp
from homeassistant.components import logbook
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

    async def _async_logbook_error(self, message: str) -> None:
        """Write a Home Assistant Logbook entry for transient or persistent fetch failures."""
        try:
            await logbook.async_log_entry(
                self.hass,
                domain="sensor",
                entity_id="sensor.kitafino",
                message=message,
            )
        except Exception:
            self.logger.exception("Kitafino-Logbuch-Eintrag konnte nicht geschrieben werden.")

    async def _async_update_data(self) -> dict[str, DayOrder]:
        last_error: Exception | None = None

        for attempt in range(1, 4):
            try:
                orders = await self.client.async_get_orders()
                self.last_successful_update = dt_util.utcnow()
                return orders
            except (aiohttp.ClientError, TimeoutError, KitafinoError) as err:
                last_error = err
                self.logger.warning(
                    "Kitafino-Abruf fehlgeschlagen (Versuch %s/3): %s",
                    attempt,
                    err,
                )
                if attempt < 3:
                    await asyncio.sleep(min(2 ** (attempt - 1), 10))
                    continue

        message = f"Kitafino-Daten konnten nicht abgerufen werden: {last_error}"
        self.logger.exception(message)
        await self._async_logbook_error(message)

        if self.data is not None:
            self.logger.warning(
                "Letzte bekannte Kitafino-Daten werden beibehalten, da der aktuelle Abruf fehlgeschlagen ist."
            )
            return self.data

        raise UpdateFailed(message) from last_error
