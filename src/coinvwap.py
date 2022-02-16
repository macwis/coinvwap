import logging
import socket
import ssl
import signal
import sys


from handshake import ProtocolHandler
from payload import split_frames
from vwap import VWAPStore


class Coinvwap:
    def __init__(self, url, product_ids) -> None:
        self.url = url
        self.product_ids = product_ids
        self.handler = ProtocolHandler(self.url, self.product_ids)
        self.vwap = VWAPStore()
        signal.signal(signal.SIGINT, self.signal_handler)
        self.sock = None

    def signal_handler(
        self, signal, frame
    ):  # pylint: disable=unused-argument,redefined-outer-name
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

    def listen(self):
        # subscribe
        logging.debug("-- Channels subscription --")
        self.sock.send(self.handler.get_subscription())

        while True:
            for payload in split_frames(self.sock.recv):
                self.vwap.store(payload)
                print(self.vwap.report(), end="")
