from homeassistant import exceptions


class DeviceNotSupported(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
