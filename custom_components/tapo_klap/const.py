# The domain of your component. Should be equal to the name of your component.
from homeassistant.const import Platform

DOMAIN = "tapo_klap"

CONF_HOST = "host"
CONF_MAC = "mac"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TRACK_DEVICE = "track_device_mac"
CONF_ADVANCED_SETTINGS = "advanced_settings"

DEFAULT_POLLING_RATE_S = 30  # 30 seconds

STEP_INIT = "user"
STEP_ADVANCED_SETTINGS = "advanced_config"

SUPPORTED_DEVICE_AS_SWITCH = [
    "p100",
    "p105",
    "p110",
    "p115",
    "p125",
    "p125m",
    "p110m",
    "tp15",
    "p100m",
    "ep25",
]

SUPPORTED_DEVICE_AS_SWITCH_POWER_MONITOR = [
    "p110",
    "p115",
    "p110m",
    "p125m",
    "ep25",
]

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH
]
"""
Platform.LIGHT
"""

HUB_PLATFORMS = [
    Platform.SIREN,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.NUMBER
]

CONF_ALTERNATIVE_IP = "ip_address"
