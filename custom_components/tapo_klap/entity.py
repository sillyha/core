from typing import TypeVar

from custom_components.tapo_klap import DOMAIN
from custom_components.tapo_klap.coordinators import TapoCoordinator
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from plugp100.responses.device_state import DeviceInfo as TapoDeviceInfo

C = TypeVar("C", bound=TapoCoordinator)


class BaseTapoEntity(CoordinatorEntity[C]):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: C):
        super().__init__(coordinator)
        self._base_data = self.coordinator.get_state_of(TapoDeviceInfo)

    @property
    def device_info(self) -> DeviceInfo:  # 注意和TapoDeviceInfo进行区分
        """展示设备信息"""
        print("<entity.py/BaseTapoEntity/device_info> Property --> deviceInfo")
        return {
            "identifiers": {(DOMAIN, self._base_data.device_id)},
            "name": self._base_data.friendly_name,
            "model": self._base_data.model,
            "manufacturer": "TP-Link@gh",
            "sw_version": self._base_data.firmware_version,
            "hw_version": self._base_data.hardware_version,
        }

    @property
    def unique_id(self):
        return self._base_data.device_id

    @callback
    def _handle_coordinator_update(self) -> None:
        self._base_data = self.coordinator.get_state_of(TapoDeviceInfo)
        self.async_write_ha_state()
        print("<entity.py/BaseTapoEntity/_handle_coordinator_update> do async_write_ha_state")
