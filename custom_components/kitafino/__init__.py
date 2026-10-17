from __future__ import annotations

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .client import KitafinoClient
from .const import DOMAIN, PLATFORMS
from .coordinator import KitafinoCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
    client = KitafinoClient(
        session,
        entry.data["username"],
        entry.data["password"],
    )
    coordinator = KitafinoCoordinator(hass, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await session.close()
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "session": session,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    runtime_data = hass.data[DOMAIN].pop(entry.entry_id)
    await runtime_data["session"].close()
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return True