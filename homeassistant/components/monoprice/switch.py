"""Switches for the Monoprice 6-Zone Amplifier."""

from __future__ import annotations

import logging

from serial import SerialException

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, MONOPRICE_OBJECT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Monoprice PA switch."""
    monoprice = hass.data[DOMAIN][entry.entry_id][MONOPRICE_OBJECT]
    async_add_entities([MonopricePASwitch(monoprice, entry.entry_id)])


class MonopricePASwitch(SwitchEntity):
    """Representation of the PA mode switch."""

    _attr_has_entity_name = True
    _attr_name = "PA Mode"

    def __init__(self, monoprice, entry_id: str) -> None:
        """Initialize the switch."""
        self._monoprice = monoprice
        self._attr_unique_id = f"{entry_id}_pa_mode"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Monoprice",
            model="6-Zone Amplifier",
            name="Monoprice 6-Zone Amplifier",
        )
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return if PA mode is enabled."""
        return self._is_on

    def turn_on(self, **kwargs) -> None:
        """Enable PA mode."""
        try:
            self._monoprice.set_pa(True)
            self._is_on = True
        except SerialException:
            _LOGGER.warning("Failed to enable PA mode")

    def turn_off(self, **kwargs) -> None:
        """Disable PA mode."""
        try:
            self._monoprice.set_pa(False)
            self._is_on = False
        except SerialException:
            _LOGGER.warning("Failed to disable PA mode")

    def update(self) -> None:
        """Fetch current state."""
        try:
            self._is_on = bool(self._monoprice.get_pa())
        except SerialException:
            _LOGGER.warning("Failed to update PA mode state")
