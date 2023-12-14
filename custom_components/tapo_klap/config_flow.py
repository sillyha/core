"""config_flow for tapo_klap integration"""
import dataclasses
import logging
from typing import Any, Optional

import aiohttp
import voluptuous as vol
from plugp100.api.tapo_client import TapoClient
from plugp100.common.credentials import AuthCredential
from plugp100.responses.device_state import DeviceInfo
from plugp100.responses.tapo_exception import (
    TapoException,
    TapoError,
)

from custom_components.tapo_klap.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_TRACK_DEVICE,
    CONF_ADVANCED_SETTINGS,
    DEFAULT_POLLING_RATE_S,
    DOMAIN,
    STEP_INIT,
    CONF_MAC, STEP_ADVANCED_SETTINGS,
)

from custom_components.tapo_klap.errors import (
    InvalidAuth,
    CannotConnect,
    InvalidHost,
)

from custom_components.tapo_klap.setup_helpers import get_host_port

from homeassistant import (
    config_entries,
    data_entry_flow,
)
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

_LOGGER = logging.getLogger(__name__)  # __name__ 是当前模块名，当模块被直接运行时模块名为 __main__ 。

STEP_USER_DATA_SCHEMA = vol.Schema(  # 数据校验器 —— 用户数据
    {
        # 需要输入字符串 #
        vol.Required(
            CONF_HOST,
            description="The IP address of your tapo device (must be static)",
        ): str,
        vol.Required(
            CONF_USERNAME,
            description="The username used with Tapo App, so your email"
        ): str,
        vol.Required(
            CONF_PASSWORD,
            description="The password used with Tapo App"
        ): str,
        # 可选框 #
        vol.Optional(
            CONF_TRACK_DEVICE,
            description="Try to track device dynamic ip using MAC address. (Your HA must be able to access to same "
                        "network of device)",
            default=False,
        ): bool,
        vol.Optional(
            CONF_ADVANCED_SETTINGS,
            description="Advanced settings"
        ): bool,
    }
)

STEP_ADVANCED_CONFIGURATION = vol.Schema(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL,
            description="Polling rate in seconds (e.g. 0.5 seconds means 500ms)",
            default=DEFAULT_POLLING_RATE_S,
        ): vol.All(vol.Coerce(float), vol.Clamp(min=0)),
    }
)


def step_options(entry: config_entries.ConfigEntry) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST,
                description="The IP address of your tapo device (must be static)",
                default=entry.data.get(CONF_HOST),
            ): str,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                description="Polling rate in seconds (e.g. 0.5 seconds means 500ms)",
                default=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_POLLING_RATE_S),
            ): vol.All(vol.Coerce(float), vol.Clamp(min=1)),
            vol.Optional(
                CONF_TRACK_DEVICE,
                description="Try to track device dynamic ip using MAC address. (Your HA must be able to access to "
                            "same network of device)",
                default=entry.data.get(CONF_TRACK_DEVICE, False),
            ): bool,
        }
    )


@dataclasses.dataclass(frozen=False)
class FirstStepData:
    state: Optional[DeviceInfo]
    user_input: Optional[dict[str, Any]]


@config_entries.HANDLERS.register(DOMAIN)
class TapoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for tapo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        super().__init__()  # ???
        self.first_step_data: Optional[FirstStepData] = None

    async def async_step_user(
            self, user_input: Optional[dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        """Handle the initial step."""
        self.hass.data.setdefault(DOMAIN, {})

        errors = {}

        if user_input is not None:
            try:
                tapo_client = await self._try_setup_api(user_input)
                device_data = await self._get_first_data_from_api(tapo_client)
                device_id = device_data.device_id
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                """Mark"""
                self.hass.data[DOMAIN][f"{device_id}_api"] = tapo_client

                """user_input: host, username, password"""
                config_entry_data = user_input | {  # 并集
                    CONF_MAC: device_data.mac,
                    CONF_SCAN_INTERVAL: DEFAULT_POLLING_RATE_S,
                    CONF_TRACK_DEVICE: user_input.pop(CONF_TRACK_DEVICE, False),
                }

                is_hub = False  # for test only
                if is_hub:  # get_short_model(device_data.model) in SUPPORTED_HUB_DEVICE_MODEL:
                    return self.async_create_entry(
                        title=f"Tapo Hub {device_data.friendly_name}",
                        data={"is_hub": True, **config_entry_data},
                    )
                elif user_input.get(CONF_ADVANCED_SETTINGS, False):
                    self.first_step_data = FirstStepData(device_data, user_input)
                    return await self.async_step_advanced_config()
                else:
                    return self.async_create_entry(
                        title=device_data.friendly_name,
                        data=config_entry_data,
                    )
            except InvalidAuth as error:
                errors["base"] = "invalid_auth"
                _LOGGER.exception("Failed to setup, invalid auth %s", str(error))
            except CannotConnect as error:
                errors["base"] = "cannot_connect"
                _LOGGER.exception("Failed to setup cannot connect %s", str(error))
            except InvalidHost as error:
                errors["base"] = "invalid_hostname"
                _LOGGER.exception("Failed to setup invalid host %s", str(error))
            except data_entry_flow.AbortFlow:
                return self.async_abort(
                    reason="already_configured"
                )
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = "unknown"
                _LOGGER.exception("Failed to setup %s", str(error), exc_info=True)

        return self.async_show_form(
            step_id=STEP_INIT,
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )

    @staticmethod
    def _raise_from_tapo_exception(exception: TapoException):
        _LOGGER.error("Tapo exception %s", str(exception.error_code))
        if exception.error_code == TapoError.INVALID_CREDENTIAL.value:
            raise InvalidAuth from exception
        else:
            raise CannotConnect from exception

    async def _try_setup_api(
            self, user_input: Optional[dict[str, Any]] = None
    ) -> TapoClient:
        if not user_input[CONF_HOST]:
            raise InvalidHost
        try:
            session = async_create_clientsession(self.hass)
            credential = AuthCredential(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            host, port = get_host_port(user_input[CONF_HOST])
            client = TapoClient.create(
                credential, address=host, port=port, http_session=session
            )
            await client.initialize()
            return client
        except TapoException as error:
            self._raise_from_tapo_exception(error)
        except (aiohttp.ClientError, Exception) as error:
            raise CannotConnect from error

    async def _get_first_data_from_api(self, tapo_client: TapoClient) -> DeviceInfo:
        try:
            return (
                (await tapo_client.get_device_info())
                .map(lambda x: DeviceInfo(**x))
                .get_or_raise()
            )
        except TapoException as error:
            self._raise_from_tapo_exception(error)
        except (aiohttp.ClientError, Exception) as error:
            raise CannotConnect from error

    async def async_step_advanced_config(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        errors = {}
        if user_input is not None:
            polling_rate = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_POLLING_RATE_S)
            return self.async_create_entry(
                title=self.first_step_data.state.friendly_name,
                data=self.first_step_data.user_input | {CONF_SCAN_INTERVAL: polling_rate},
            )
        else:
            return self.async_show_form(
                step_id=STEP_ADVANCED_SETTINGS,
                data_schema=STEP_ADVANCED_CONFIGURATION,
                errors=errors,
            )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        _LOGGER.info(config_entry)
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        """Manage the options."""
        if user_input is not None:
            """
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self.config_entry.data | user_input
            )
            """
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "show_things",
                        default=self.config_entry.options.get("show_things"),
                    ): bool
                }
            ),
        )
