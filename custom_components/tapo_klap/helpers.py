import ipaddress
from typing import Optional

from homeassistant.components.network import Adapter


def get_network_of(adapter: Adapter) -> Optional[str]:
    if len(adapter.get("ipv4")) > 0:
        return f"{adapter.get('ipv4')[0].get('address')}/{adapter.get('ipv4')[0].get('network_prefix')}"
    return None


async def find_adapter_for(
    adapters: list[Adapter], ip: Optional[str]
) -> Optional[Adapter]:
    default_enabled = next(
        iter(
            [
                adapter
                for adapter in adapters
                if adapter.get("enabled") and adapter.get("default")
            ]
        ),
        None,
    )

    if ip is None:  # search for adapter enabled and default
        return default_enabled
    else:
        for adapter in adapters:
            if adapter.get("enabled") and len(adapter.get("ipv4")) > 0:
                adapter_network = get_network_of(adapter)
                if ipaddress.ip_address(ip) in ipaddress.IPv4Network(adapter_network, strict=False):
                    return adapter

    return default_enabled
