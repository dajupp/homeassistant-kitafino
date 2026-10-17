from __future__ import annotations

from pathlib import Path

import aiohttp
import voluptuous as vol
from homeassistant import config_entries

from .client import KitafinoAuthError, KitafinoClient, KitafinoError
from .const import DOMAIN


def _read_credentials(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = value.split("#", 1)[0].strip()
        values[key.strip()] = value

    username = values.get("username", "")
    password = values.get("password", "")
    if not username or not password:
        raise ValueError("Die Schlüssel username und password müssen gesetzt sein.")
    return {"username": username, "password": password}


class KitafinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            try:
                credentials = _read_credentials(Path(self.hass.config.path(".env")))
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    client = KitafinoClient(
                        session,
                        credentials["username"],
                        credentials["password"],
                    )
                    await client.async_get_orders()
            except FileNotFoundError:
                errors["base"] = "env_not_found"
            except ValueError:
                errors["base"] = "invalid_env"
            except KitafinoAuthError:
                errors["base"] = "invalid_auth"
            except KitafinoError:
                errors["base"] = "cannot_connect"
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Kitafino", data=credentials)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )