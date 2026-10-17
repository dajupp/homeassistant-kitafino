from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
import re
from urllib.parse import urljoin

import aiohttp

from .const import LOGIN_URL, WEEKDAYS


class KitafinoError(Exception):
    """Base error for Kitafino communication and page parsing."""


class KitafinoAuthError(KitafinoError):
    """Kitafino rejected the login or the session expired."""


@dataclass(frozen=True)
class DayOrder:
    ordered: bool
    service_date: date | None


class _Node:
    def __init__(self, tag: str = "", attrs: list[tuple[str, str | None]] | None = None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children: list[_Node | str] = []


class _DocumentParser(HTMLParser):
    _VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.root = _Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self._VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack[-1].children.append(_Node(tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def _walk(node: _Node):
    for child in node.children:
        if isinstance(child, _Node):
            yield child
            yield from _walk(child)


def _text(node: _Node) -> str:
    return "".join(child if isinstance(child, str) else _text(child) for child in node.children)


def _parse(html: str) -> _Node:
    parser = _DocumentParser()
    parser.feed(html)
    return parser.root


def _login_form(root: _Node) -> _Node | None:
    return next(
        (
            node
            for node in _walk(root)
            if node.tag == "form" and "do_login" in node.attrs.get("action", "")
        ),
        None,
    )


def _service_date(content: str) -> date | None:
    match = re.search(
        r"(?<!\d)(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{2}-\d{2})(?!\d)",
        content,
    )
    if match is None:
        return None

    value = match.group()
    date_format = "%d.%m.%Y" if "." in value else "%Y-%m-%d"
    try:
        return datetime.strptime(value, date_format).date()
    except ValueError:
        return None


def parse_orders(html: str) -> dict[str, DayOrder]:
    """Return order status and service date for each weekday."""
    orders = {key: DayOrder(False, None) for key, _ in WEEKDAYS}
    root = _parse(html)
    tables = [
        node
        for node in _walk(root)
        if "order_table" in node.attrs.get("class", "").split()
    ]
    if not tables:
        raise KitafinoError("Kitafino hat keine Bestelltabellen geliefert.")

    for table in tables:
        table_text = _text(table)
        content = table_text.casefold()
        service_date = _service_date(table_text)
        markers = any(
            {"bestellt_check", "success", "icon_check"}.issubset(
                set(node.attrs.get("class", "").split())
            )
            for node in _walk(table)
        )
        for key, day in WEEKDAYS:
            if day.casefold() in content:
                previous = orders[key]
                orders[key] = DayOrder(
                    ordered=previous.ordered or markers,
                    service_date=previous.service_date or service_date,
                )

    return orders


class KitafinoClient:
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._orders_url: str | None = None

    async def _login(self) -> str:
        async with self._session.get(LOGIN_URL) as response:
            response.raise_for_status()
            root = _parse(await response.text())

        form = _login_form(root)
        if form is None:
            raise KitafinoAuthError("Kitafino-Loginformular wurde nicht gefunden.")

        fields = {
            node.attrs["name"]: node.attrs.get("value", "") or ""
            for node in _walk(form)
            if node.tag == "input"
            and node.attrs.get("name")
            and node.attrs.get("type", "").lower() == "hidden"
        }
        fields.update({"benutzername": self._username, "passwort": self._password})
        login_url = urljoin(LOGIN_URL, form.attrs.get("action", LOGIN_URL))
        async with self._session.post(
            login_url,
            data=fields,
            headers={"Referer": LOGIN_URL},
        ) as response:
            response.raise_for_status()
            html = await response.text()
            self._orders_url = str(response.url)

        if _login_form(_parse(html)) is not None:
            raise KitafinoAuthError("Kitafino hat die Anmeldung abgelehnt.")
        return html

    async def async_get_orders(self) -> dict[str, bool]:
        if self._orders_url is None:
            html = await self._login()
            return parse_orders(html)

        async with self._session.get(self._orders_url) as response:
            response.raise_for_status()
            html = await response.text()

        if _login_form(_parse(html)) is not None:
            html = await self._login()
        return parse_orders(html)