"""Test Monoprice switches."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.monoprice.const import CONF_PORT, CONF_SOURCES, DOMAIN
from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry, snapshot_platform

MOCK_CONFIG = {CONF_PORT: "fake port", CONF_SOURCES: {}}


class MockMonoprice:
    """Mock for pymonoprice object for switch tests."""

    def __init__(self) -> None:
        """Initialize the mock."""
        self.pa = False

    def set_pa(self, enabled: bool) -> None:
        """Set the PA mode state."""
        self.pa = enabled

    def get_pa(self) -> bool:
        """Return the current PA mode state."""
        return self.pa


@pytest.mark.parametrize("load_platforms", [[Platform.SWITCH]])
async def test_pa_switch(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the PA mode switch."""
    monoprice = MockMonoprice()

    with patch(
        "homeassistant.components.monoprice.get_monoprice",
        new=lambda *a: monoprice,
    ):
        config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
        config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    await snapshot_platform(hass, entity_registry, snapshot, config_entry.entry_id)

    with patch.object(monoprice, "set_pa") as mock_set_pa:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "switch.pa_mode"},
            blocking=True,
        )
        mock_set_pa.assert_called_once_with(True)

    with patch.object(monoprice, "set_pa") as mock_set_pa:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "switch.pa_mode"},
            blocking=True,
        )
        mock_set_pa.assert_called_once_with(False)
