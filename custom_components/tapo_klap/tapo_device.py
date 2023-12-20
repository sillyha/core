from dataclasses import dataclass
from datetime import timedelta

from plugp100.api.tapo_client import TapoClient

from custom_components.tapo_klap.const import DEFAULT_POLLING_RATE_S, CONF_HOST, DOMAIN, PLATFORMS
from custom_components.tapo_klap.coordinators import create_coordinator, HassTapoDeviceData
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant


async def _on_options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    print("<tapo_device.py/_on_options_update_listener> config_entry update!! entry_id: ", config_entry.entry_id)
    await hass.config_entries.async_reload(config_entry.entry_id)


@dataclass
class TapoDevice:
    entry: ConfigEntry
    client: TapoClient

    async def initialize_device(self, hass: HomeAssistant) -> bool:
        print("<tapo_device.py/initialize_device> enter...")
        polling_rate = timedelta(
            seconds=self.entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_POLLING_RATE_S)
        )

        host = self.entry.data.get(CONF_HOST)

        coordinator = (
            await create_coordinator(hass, self.client, host, polling_rate)
        ).get_or_raise()
        print("<tapo_device.py/initialize_device> async_config_entry_first_refresh")
        # Fetch initial data so we have data when entities subscribe
        #
        # If the refresh fails, async_config_entry_first_refresh will
        # raise ConfigEntryNotReady and setup will try again later
        #
        # If you do not want to retry setup on failure, use
        # coordinator.async_refresh() instead
        await coordinator.async_config_entry_first_refresh()  # could raise ConfigEntryNotReady

        print("<tapo_device.py/initialize_device> storing --> hass.data[DOMAIN][self.entry.entry_id] = HassTapoDeviceData()")
        hass.data[DOMAIN][self.entry.entry_id] = HassTapoDeviceData(
            coordinator=coordinator,
            config_entry_update_unsub=self.entry.add_update_listener(
                _on_options_update_listener
            ),
            child_coordinators=[],
        )

        print("<tapo_device.py/initialize_device> forward config_entry to platforms --> async_forward_entry_setups")
        await hass.config_entries.async_forward_entry_setups(self.entry, PLATFORMS)
        return True
