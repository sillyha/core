from typing import Optional, Dict, Any, cast

from plugp100.responses.device_state import PlugDeviceState

from custom_components.tapo_klap.setup_helpers import setup_from_platform_config
from custom_components.tapo_klap import DOMAIN
from custom_components.tapo_klap.coordinators import PlugTapoCoordinator, HassTapoDeviceData
from custom_components.tapo_klap.entity import BaseTapoEntity
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class TapoPlugEntity(BaseTapoEntity[PlugTapoCoordinator], SwitchEntity):
    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(self, coordinator: PlugTapoCoordinator):
        super().__init__(coordinator)

    @property
    def is_on(self) -> Optional[bool]:
        return self.coordinator.get_state_of(PlugDeviceState).device_on  # 注意property仅读取本地状态不进行IO

    async def async_turn_on(self, **kwargs):
        (await self.coordinator.device.on()).get_or_raise()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        (await self.coordinator.device.off()).get_or_raise()
        await self.coordinator.async_request_refresh()


async def async_setup_platform(
        hass: HomeAssistant,
        config: Dict[str, Any],
        async_add_entities: AddEntitiesCallback,
        discovery_info=None,
) -> None:
    """await hass.config_entries.async_forward_entry_setups(self.entry, PLATFORMS)

    for above function called in __init__.py, this function() will not be called.
    """
    print("<switch.py/async_setup_platform> enter...")
    coordinator = await setup_from_platform_config(hass, config)
    if isinstance(coordinator, PlugTapoCoordinator):
        print("<switch.py/async_setup_platform> async_add_entities")
        async_add_entities([TapoPlugEntity(coordinator)], True)


async def async_setup_device_switch(
        hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    print("<switch.py/async_setup_device_switch> enter...")
    data = cast(HassTapoDeviceData, hass.data[DOMAIN][entry.entry_id])
    if isinstance(data.coordinator, PlugTapoCoordinator):
        async_add_devices([TapoPlugEntity(data.coordinator)], True)
    """
    elif isinstance(data.coordinator, PowerStripCoordinator):
        async_add_devices(
            [
                StripPlugEntity(data.coordinator, child.device_id)
                for child in data.coordinator.get_children()
            ],
            True,
        )
    """


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """
    # get tapo helper
    if entry.data.get("is_hub", False):
        await async_setup_hub_switch(hass, entry, async_add_entities)
    else:
        await async_setup_device_switch(hass, entry, async_add_entities)
    """
    print("<switch.py/async_setup_entry> enter...")
    await async_setup_device_switch(hass, entry, async_add_entities)
