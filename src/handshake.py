from __future__ import annotations

import ipaddress
import json
import uuid
from typing import List, Dict
from urllib.parse import urlsplit

from subscribe import ABNF


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

    def _get_switch_headers(self) -> Dict:
        self.host, self.port, self.is_secure = self._get_switch_headers_parts()

        self.headers = {}
        self.headers["Host"] = self.build_host(self.host, self.port, self.is_secure)
        self.headers["Upgrade"] = "websocket"
        self.headers["Connection"] = "Upgrade"
        self.headers["Sec-WebSocket-Key"] = self.sec_websocket_key
        self.headers["Sec-WebSocket-Protocol"] = "chat, superchat"
        self.headers["Sec-WebSocket-Version"] = "13"
        return self.headers

    def get_switch_headers(self) -> bytes:
        return str(
            ("".join(f"{key}: {value}\r\n" for key, value in self.headers.items()))
            + "\r\n"
        ).encode()

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
