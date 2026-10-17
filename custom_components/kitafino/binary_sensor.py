from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, WEEKDAYS
from .coordinator import KitafinoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = [
        KitafinoOrderSensor(coordinator, entry, index, key, day)
        for index, (key, day) in enumerate(WEEKDAYS, start=1)
    ]
    entities.append(KitafinoTodaySensor(coordinator, entry))
    async_add_entities(entities)


class KitafinoOrderSensor(CoordinatorEntity[KitafinoCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:food-takeout-box"

    def __init__(
        self,
        coordinator: KitafinoCoordinator,
        entry: ConfigEntry,
        weekday_index: int,
        weekday_key: str,
        weekday_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._weekday_key = weekday_key
        self._attr_name = f"{weekday_index:02d} {weekday_name} Essen bestellt"
        self._attr_unique_id = f"{entry.entry_id}_{weekday_key}_ordered"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Kitafino",
            manufacturer="Kitafino",
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data[self._weekday_key].ordered


class KitafinoTodaySensor(CoordinatorEntity[KitafinoCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "00 Heute Essen bestellt"
    _attr_icon = "mdi:food-takeout-box"

    def __init__(self, coordinator: KitafinoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_today_ordered"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Kitafino",
            manufacturer="Kitafino",
        )

    @property
    def is_on(self) -> bool:
        weekday_index = dt_util.now().weekday()
        if weekday_index >= len(WEEKDAYS):
            return False
        weekday_key, _ = WEEKDAYS[weekday_index]
        return self.coordinator.data[weekday_key].ordered