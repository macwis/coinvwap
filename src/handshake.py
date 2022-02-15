from __future__ import annotations

import ipaddress
from typing import Dict, Iterable, List, Mapping, MutableMapping, Tuple, Union
from urllib.parse import urlsplit

__all__ = ["Headers", "HeadersLike"]


class Headers(MutableMapping[str, str]):
    def __init__(self, *args: HeadersLike, **kwargs: str) -> None:
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
        if len(value) == 1:
            return value[0]
        else:
            # TODO: implement custom specific exception
            raise Exception(f"No key for {key}!")

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


url = "wss://ws-feed.exchange.coinbase.com/"
origin = "http://ws-feed.exchange.coinbase.com"
parsed_url = urlsplit(url)
is_secure = parsed_url.scheme in ["https", "wss"]
host = parsed_url.hostname
port = parsed_url.port or (443 if is_secure else 80)
path = parsed_url.path
if parsed_url.query:
    path += "?" + parsed_url.query

headers = Headers()
headers["Host"] = build_host(host, port, is_secure)
headers["Origin"] = origin
headers["Upgrade"] = "websocket"
headers["Connection"] = "Upgrade"
headers["Sec-WebSocket-Key"] = "dGhl43NhbXBsZSBub25jZQ=="
headers["Sec-WebSocket-Protocol"] = "chat, superchat"
headers["Sec-WebSocket-Version"] = "13"
