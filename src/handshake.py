from __future__ import annotations

import ipaddress
import json
import uuid
from typing import (Dict, Iterable, Iterator, List, Mapping, MutableMapping,
                    Tuple, Union)
from urllib.parse import urlsplit

from subscribe import ABNF

__all__ = ["Headers", "HeadersLike", "ProtocolHandler"]


class Headers(MutableMapping[str, str]):
    """
    This class has been borrowed from websocket-client.
    It is used to get proper headers around the subscribe request.
    """

    def __init__(
        self, *args: HeadersLike, **kwargs: str  # pylint: disable=unused-argument
    ) -> None:
        self._dict: Dict[str, List[str]] = {}
        self._list: List[Tuple[str, str]] = []
        self.__setitem__(key="", value="")

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    # MutableMapping methods

    def __getitem__(self, key: str) -> str:
        value = self._dict[key.lower()]
        if len(value) != 1:
            # TODO: implement custom specific exception
            raise Exception(f"No key for {key}!")
        return value[0]

    def __setitem__(self, key: str, value: str) -> None:
        self._dict.setdefault(key.lower(), []).append(value)
        self._list.append((key, value))

    def __delitem__(self, key: str) -> None:
        key_lower = key.lower()
        self._dict.__delitem__(key_lower)
        # This is inefficient. Fortunately deleting HTTP headers is uncommon.
        self._list = [(k, v) for k, v in self._list if k.lower() != key_lower]

    def __str__(self) -> str:
        return "".join(f"{key}: {value}\r\n" for key, value in self._list) + "\r\n"

    def serialize(self) -> bytes:
        return str(self).encode()


HeadersLike = Union[Headers, Mapping[str, str], Iterable[Tuple[str, str]]]


class ProtocolHandler:  # pylint: disable=too-many-instance-attributes
    """
    Used to handle handshake of the switch from HTTP(S) to websocket.py
    It also wraps the sending of the subscription with Headers.
    """
    def __init__(self, url: str, product_ids: List[str], channel: str) -> None:
        self.url = url
        self.product_ids = product_ids
        self.sec_websocket_key = f"{uuid.uuid4()}=="
        self.switch_headers = self._get_switch_headers()
        self.channel = channel

    def _get_switch_headers_parts(self):
        parsed_url = urlsplit(self.url)
        is_secure = parsed_url.scheme in ["https", "wss"]
        host = parsed_url.hostname
        port = parsed_url.port or (443 if is_secure else 80)
        path = parsed_url.path
        if parsed_url.query:
            path += "?" + parsed_url.query
        return (host, port, is_secure)

    def _get_switch_headers(self) -> Headers:
        self.host, self.port, self.is_secure = self._get_switch_headers_parts()

        headers = Headers()
        headers["Host"] = self.build_host(self.host, self.port, self.is_secure)
        headers["Upgrade"] = "websocket"
        headers["Connection"] = "Upgrade"
        headers["Sec-WebSocket-Key"] = self.sec_websocket_key
        headers["Sec-WebSocket-Protocol"] = "chat, superchat"
        headers["Sec-WebSocket-Version"] = "13"
        return headers

    def get_switch_headers(self) -> bytes:
        return self.switch_headers.serialize()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_is_secure(self):
        return self.is_secure

    def get_init_request(self) -> str:
        init_request = "GET / HTTP/1.1\r\n".encode()
        init_request += self.get_switch_headers()
        return init_request

    def get_subscription(self) -> bytes:
        params = {
            "type": "subscribe",
            "product_ids": self.product_ids,
            "channels": [
                "heartbeat",
                {"name": self.channel, "product_ids": self.product_ids},
            ],
        }
        subscribe = ABNF.create_frame(json.dumps(params), 0x1, fin=1)
        return subscribe.format()

    @staticmethod
    def build_host(host: str, port: int, secure: bool) -> str:
        """
        Build a ``Host`` header.
        """
        # https://www.rfc-editor.org/rfc/rfc3986.html#section-3.2.2
        # IPv6 addresses must be enclosed in brackets.
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            # host is a hostname
            pass
        else:
            # host is an IP address
            if address.version == 6:
                host = f"[{host}]"

        if port != (443 if secure else 80):
            host = f"{host}:{port}"

        return host
