import logging

from plugp100.api.tapo_client import TapoClient
from plugp100.common.credentials import AuthCredential
from plugp100.discovery.local_device_finder import LocalDeviceFinder

from custom_components.tapo_klap.const import CONF_USERNAME, CONF_PASSWORD, CONF_TRACK_DEVICE, CONF_MAC, CONF_HOST, \
    DOMAIN
from custom_components.tapo_klap.helpers import find_adapter_for, get_network_of
from homeassistant.components import network
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


def get_host_port(host_user_input: str) -> (str, int):
    if ":" in host_user_input:
        parts = host_user_input.split(":", 1)
        return parts[0], int(parts[1])

    return host_user_input, 80


async def try_track_ip_address(
    hass: HomeAssistant, mac: str, last_known_ip: str
) -> str:
    _LOGGER.info(
        "Trying to track ip address of %s, last known ip is %s", mac, last_known_ip
    )

    adapters = await network.async_get_adapters(hass)
    adapter = await find_adapter_for(adapters, last_known_ip)
    try:
        if adapter is not None:
            target_network = get_network_of(adapter)
            """本地发现"""
            device = await LocalDeviceFinder.scan_one(mac.replace("-", ":"), target_network, timeout=5)
            return device.get_or_else(last_known_ip)
        else:
            _LOGGER.warning(
                "No adapter found for %s with last ip %s", mac, last_known_ip
            )
    except PermissionError:
        _LOGGER.warning("No permission to scan network")

    return last_known_ip


async def connect_tapo_client(
    hass: HomeAssistant, credentials: AuthCredential, ip_address: str, unique_id: str
) -> TapoClient:
    api = (
        hass.data[DOMAIN][f"{unique_id}_api"]
        if f"{unique_id}_api" in hass.data[DOMAIN]
        else None
    )
    if api is not None:
        _LOGGER.debug("Re-using setup API to create a coordinator")
    else:
        _LOGGER.debug("Creating new API to create a coordinator for %s", unique_id)
        session = async_get_clientsession(hass)
        host, port = get_host_port(ip_address)
        api = TapoClient.create(
            credentials, address=host, port=port, http_session=session
        )
        await api.initialize()
    return api


async def setup_tapo_api(hass: HomeAssistant, config: ConfigEntry) -> TapoClient:
    credential = AuthCredential(
        config.data.get(CONF_USERNAME), config.data.get(CONF_PASSWORD)
    )

    if config.data.get(CONF_TRACK_DEVICE, False) and config.data.get(CONF_MAC, None) is not None:
        if config.data.get(CONF_MAC, None) is not None:
            address = await try_track_ip_address(
                hass, config.data.get(CONF_MAC), config.data.get(CONF_HOST)
            )
        else:
            logging.warning(
                "Tracking mac address enabled, but no MAC address found on config entry"
            )
            address = config.data.get(CONF_HOST)
    else:
        address = config.data.get(CONF_HOST)

    return await connect_tapo_client(
        hass,
        credential,
        address,
        config.unique_id,
    )

