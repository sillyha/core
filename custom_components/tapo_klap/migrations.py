from plugp100.common.credentials import AuthCredential

from custom_components.tapo_klap.const import CONF_USERNAME, CONF_HOST, CONF_PASSWORD, DEFAULT_POLLING_RATE_S, CONF_MAC, \
    CONF_TRACK_DEVICE
from custom_components.tapo_klap.setup_helpers import connect_tapo_client
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant


async def migrate_entry_to_v6(hass: HomeAssistant, config_entry: ConfigEntry):
    credential = AuthCredential(
        config_entry.data.get(CONF_USERNAME), config_entry.data.get(CONF_PASSWORD)
    )

    api = await connect_tapo_client(
        hass, credential, config_entry.data.get(CONF_HOST), config_entry.unique_id
    )

    new_data = {**config_entry.data}
    scan_interval = new_data.pop(CONF_SCAN_INTERVAL, DEFAULT_POLLING_RATE_S)
    mac = (await api.get_device_info()).map(lambda j: j["mac"]).get_or_else(None)

    config_entry.version = 6

    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **new_data,
            CONF_MAC: mac,
            CONF_TRACK_DEVICE: False,
            CONF_SCAN_INTERVAL: scan_interval,
        },
    )
