from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, OptionsFlowWithReload
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .client import KitafinoAuthError, KitafinoClient, KitafinoError
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


_USERNAME_SELECTOR = TextSelector(
    TextSelectorConfig(
        type=TextSelectorType.TEXT,
        autocomplete="username",
    )
)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): _USERNAME_SELECTOR,
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        ),
    }
)
STEP_RECONFIGURE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): _USERNAME_SELECTOR,
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="new-password",
            )
        ),
    }
)


class KitafinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        return KitafinoOptionsFlow()

    async def _async_validate_credentials(self, credentials: dict[str, str]) -> str | None:
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                client = KitafinoClient(
                    session,
                    credentials[CONF_USERNAME],
                    credentials[CONF_PASSWORD],
                )
                await client.async_get_orders()
        except KitafinoAuthError:
            return "invalid_auth"
        except KitafinoError:
            return "cannot_connect"
        except (aiohttp.ClientError, TimeoutError):
            return "cannot_connect"
        return None

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            credentials = {
                CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }
            error = await self._async_validate_credentials(credentials)
            if error is None:
                return self.async_create_entry(title="Kitafino", data=credentials)
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict | None = None):
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            credentials = {
                CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }
            error = await self._async_validate_credentials(credentials)
            if error is None:
                return self.async_update_reload_and_abort(entry, data=credentials)
            errors["base"] = error

        schema = self.add_suggested_values_to_schema(
            STEP_RECONFIGURE_DATA_SCHEMA,
            {CONF_USERNAME: entry.data[CONF_USERNAME]},
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )


class KitafinoOptionsFlow(OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            DEFAULT_SCAN_INTERVAL,
                        ),
                    ): vol.All(
                        NumberSelector(
                            NumberSelectorConfig(
                                min=MIN_SCAN_INTERVAL,
                                max=MAX_SCAN_INTERVAL,
                                step=1,
                                mode=NumberSelectorMode.BOX,
                                unit_of_measurement="min",
                            )
                        ),
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    )
                }
            ),
        )