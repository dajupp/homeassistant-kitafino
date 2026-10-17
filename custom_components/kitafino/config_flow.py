from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .client import KitafinoAuthError, KitafinoClient, KitafinoError
from .const import DOMAIN


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