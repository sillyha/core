"""The "tapo_klap" custom component.

Configuration:
To use this component you will need to add the following to your configuration.yaml file.
    "tapo_klap:"
"""

from __future__ import annotations

import datetime
import logging

import voluptuous as vol
from plugp100.responses.device_state import DeviceInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.json import JsonObjectType

from .const import DOMAIN
from .errors import DeviceNotSupported
from .setup_helpers import setup_tapo_api
from .tapo_device import TapoDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the tapo_klap component."""
    hass.data.setdefault(DOMAIN, {})
    print("<__init__.py/async_setup>[tapo_klap]")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up tapo_klap from a config entry."""
    print("<__init__.py/async_setup_entry>[tapo_klap]")
    hass.data.setdefault(DOMAIN, {})
    try:
        api = await setup_tapo_api(hass, entry)
        """
        state = (
            (await api.get_device_info()).map(lambda x: DeviceInfo(**x)).get_or_raise()
        )
        if get_short_model(state.model) in SUPPORTED_HUB_DEVICE_MODEL:
            hub = TapoHub(
                entry,
                HubDevice(api, subscription_polling_interval_millis=30_000),
            )
            return await hub.initialize_hub(hass)
        else:
            device = TapoDevice(entry, api)
            return await device.initialize_device(hass)
        """
        device = TapoDevice(entry, api)
        return await device.initialize_device(hass)
    except DeviceNotSupported as error:
        raise error
    except Exception as error:
        raise ConfigEntryNotReady from error


'''
ATTR_NAME = "name"
DEFAULT_NAME = "K-L-A-P"

SEARCH_ITEMS_SERVICE_NAME = "search_items"
SEARCH_ITEMS_SCHEMA = vol.Schema({
    vol.Required("start"): datetime.datetime,
    vol.Required("end"): datetime.datetime,
})

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up is called when Home Assistant is loading our component."""

    def handle_demo_service(call):
        """Handle the service call."""
        name = call.data.get(ATTR_NAME, DEFAULT_NAME)
        print("[gh_test] name: %s", name)

        hass.states.set("tapo_klap.klap_supported", name)

    hass.services.register(DOMAIN, "demo_service", handle_demo_service)

    async def search_items(call: ServiceCall) -> ServiceResponse:
        """Search in the date range and return the matching items."""
        # items = await my_client.search(call.data["start"], call.data["end"])
        items = []
        return {
            "items": [
                {
                    "summary": item["summary"],
                    "description": item["description"],
                } for item in items
            ],
        }

    hass.services.async_register(
        DOMAIN,
        SEARCH_ITEMS_SERVICE_NAME,
        search_items,
        schema=SEARCH_ITEMS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.set("tapo_klap.klap_supported", "TODO...")

    print("[gh_test] component tapo_klap setup...")

    # Return boolean to indicate that initialization was successfully.
    return True
'''
