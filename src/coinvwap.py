import logging
import signal
import socket
import ssl
import sys
from typing import List

from handshake import ProtocolHandler
from payload import split_frames
from vwap import VWAPStore


class Coinvwap:
    """
    Main class handling the connection and websocket listening.
    listen method can be used with threading.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        product_ids: List[str] or None = None,
        url: str = "wss://ws-feed.exchange.coinbase.com/",
        channel: str = "ticker",
        type_field: str = "ticker",
        price_field: str = "price",
        quantity_field: str = "last_size",
    ) -> None:
        self.url = url
        if product_ids:
            self.product_ids = product_ids
        else:
            self.product_ids = ["BTC-USD", "ETH-USD", "ETH-BTC"]
        self.channel = channel
        self.handler = ProtocolHandler(self.url, self.product_ids, self.channel)
        self.vwap = VWAPStore(
            product_ids=self.product_ids,
            price_field=price_field,
            quantity_field=quantity_field,
            type_field=type_field,
        )
        signal.signal(signal.SIGINT, self.signal_handler)
        self.sock = None
        self.connected = False

    def signal_handler(
        self, signal, frame
    ):  # pylint: disable=unused-argument,redefined-outer-name
        self.connected = False
        print("\r-- Interrupted by the user --")
        self.sock.close()
        print("-- Exiting --")
        sys.exit(0)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.handler.get_is_secure():
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
            self.sock = ssl_context.wrap_socket(
                self.sock, server_hostname=self.handler.get_host()
            )
        self.sock.connect((self.handler.get_host(), self.handler.get_port()))
        self._switch_protocol()
        self.connected = True

    def _switch_protocol(self):
        # HTTP request to switch protocol to websocket
        logging.debug(self.handler.get_init_request())
        self.sock.send(self.handler.get_init_request())

        # Expected confirmation: 101 Switching Protocols
        data = self.sock.recv(1024)
        logging.debug(data)
        if "HTTP/1.1 101 Switching Protocols" not in str(data):
            # TODO: make a nice custom Exception
            raise Exception("Switching protocols failed!")
        logging.debug("-- Switched to websockets --")

    def listen(self, report_fn=None, buffer=None):
        # subscribe
        logging.debug("-- Channels subscription --")
        self.sock.send(self.handler.get_subscription())

        while self.connected:
            for payload in split_frames(self.sock.recv):
                self.vwap.store(payload)
                if report_fn:
                    report_fn(self.vwap.report(point_counts=True), end="")
                if buffer:
                    buffer += self.vwap.report(point_counts=True)

    def disconnect(self):
        self.connected = False
