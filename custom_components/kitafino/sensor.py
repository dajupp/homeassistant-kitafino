from __future__ import annotations

from datetime import date, datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WEEKDAYS
from .coordinator import KitafinoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = [
        KitafinoDateSensor(coordinator, entry, index, key, day)
        for index, (key, day) in enumerate(WEEKDAYS, start=1)
    ]
    entities.append(KitafinoLastUpdateSensor(coordinator, entry))
    async_add_entities(entities)


class KitafinoDateSensor(CoordinatorEntity[KitafinoCoordinator], SensorEntity):
    _attr_device_class = SensorDeviceClass.DATE
    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar"

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
        self._attr_name = f"{weekday_index:02d} {weekday_name} Datum"
        self._attr_unique_id = f"{entry.entry_id}_{weekday_key}_date"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Kitafino",
            manufacturer="Kitafino",
        )

    @property
    def native_value(self) -> date | None:
        return self.coordinator.data[self._weekday_key].service_date


class KitafinoLastUpdateSensor(CoordinatorEntity[KitafinoCoordinator], SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True
    _attr_icon = "mdi:cloud-check-outline"
    _attr_name = "Letzter erfolgreicher Abruf"

    def __init__(self, coordinator: KitafinoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_successful_update"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Kitafino",
            manufacturer="Kitafino",
        )

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_successful_update