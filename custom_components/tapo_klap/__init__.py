"""
The "tapo_klap" custom component.

Configuration:
To use this component you will need to add the following to your configuration.yaml file.
    "tapo_klap:"
"""

from __future__ import annotations

import datetime

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.json import JsonObjectType

from .const import DOMAIN

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

