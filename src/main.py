import json
import logging
import socket
import ssl
import time

from handshake import headers, host, is_secure, port
from subscribe import ABNF

request = f"GET / HTTP/1.1\r\n".encode()
request += headers.serialize()

params = {
    "type": "subscribe",
    "product_ids": ["BTC-USD", "ETH-USD", "ETH-BTC"],
    "channels": [
        "heartbeat",
        {"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD", "ETH-BTC"]},
    ],
}
subscribe = ABNF.create_frame(json.dumps(params), 0x1, fin=1)


def split_frames(recv_fn, recv_buffer=4096):
    msg = recv_fn(recv_buffer)
    logging.debug("-- Msg size --", len(msg))
    carret = 0
    while carret < len(msg):
        logging.debug("-- Carret --", carret)
        logging.debug("-- Msg left --", msg[carret:])
        if len(msg) - carret < 4:
            # Payload too short to make sense, let's read more data
            # TODO: test cover various partial-frame cases!
            msg += recv_fn(recv_buffer)
        # fin, rsv1, rsv2, rsv3, opcode
        # expected fin=1, rsv*=0, opcode=0x1 (OPCODE_TEXT)
        if "{:08b}".format(msg[carret]) == "10000001":
            length = msg[carret + 2] << 8 | msg[carret + 3]
            logging.debug("-- Crop length --", length)
            content = msg[carret + 4 : carret + length + 4]
            logging.debug("-- Crop --", content)
            try:
                parsed = json.loads(content)
                yield parsed
                carret = carret + 4 + length
            except json.decoder.JSONDecodeError:
                logging.debug("Buffer was short, reading in more ..")
                msg += recv_fn(recv_buffer)


def vwap(p, q):
    if len(q) == 0:
        return 0.0
    return sum([pj * qj for pj, qj in zip(p, q)]) / sum(q)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if is_secure:
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        sock = ssl_context.wrap_socket(sock, server_hostname=host)

    sock.connect((host, port))

    # HTTP request to switch protocol to websocket
    logging.debug(request)
    sock.send(request)

    # Expected confirmation: 101 Switching Protocols
    data = sock.recv(1024)
    logging.debug(data)
    if "HTTP/1.1 101 Switching Protocols" not in str(data):
        raise Exception("Switching protocols failed!")
    else:
        logging.debug("-- Switched to websockets --")

    time.sleep(1)

    # subscribe
    logging.debug("-- Channels subscription --", subscribe)
    sock.send(subscribe.format())

    from collections import deque

    prices_n_vols = {
        "BTC-USD": deque(maxlen=200),
        "ETH-USD": deque(maxlen=200),
        "ETH-BTC": deque(maxlen=200),
    }

    while True:
        time.sleep(1)
        # recv_buffer = []
        # recv_pack = recv_strict(sock.recv, recv_buffer)
        for payload in split_frames(sock.recv):
            logging.debug("\n\n", payload)
            if payload["type"] == "ticker":
                prices_n_vols[payload["product_id"]].append(
                    (
                        float(payload["price"]),
                        float(payload["last_size"]),
                    )
                )

        for product_id in prices_n_vols.keys():
            prices = [val[0] for val in prices_n_vols[product_id]]
            vols = [val[1] for val in prices_n_vols[product_id]]
            print(
                f"{product_id}\t{'{:010f}'.format(vwap(prices, vols))}\tpoints:\t{len(prices_n_vols[product_id])}"
            )

    # sock.close()


"""
Framing protocol specs:
    https://datatracker.ietf.org/doc/html/rfc6455#section-5.2

raw_sub = b'\x81\xfe\x00\x87\x16\x98\xa4\xe7m\xba\xd0\x9ef\xfd\x86\xdd6\xba\xd7\x92t\xeb\xc7\x95\x7f\xfa\xc1\xc5:\xb8\x86\x97d\xf7\xc0\x92u\xec\xfb\x8er\xeb\x86\xdd6\xc3\x86\xa5B\xdb\x89\xb2E\xdc\x86\xba:\xb8\x86\x84~\xf9\xca\x89s\xf4\xd7\xc5,\xb8\xff\xc5~\xfd\xc5\x95b\xfa\xc1\x86b\xba\x88\xc7m\xba\xca\x86{\xfd\x86\xdd6\xba\xd0\x8eu\xf3\xc1\x954\xb4\x84\xc5f\xea\xcb\x83c\xfb\xd0\xb8\x7f\xfc\xd7\xc5,\xb8\xff\xc5T\xcc\xe7\xcaC\xcb\xe0\xc5:\xb8\x86\xa5B\xdb\x89\xa0T\xc8\x86\xbak\xc5\xd9'
print("{:03b}".format(raw_sub[0]))
# gives: '10000001'

fin: 1
rsv1: 0
rsv2: 0
rsv3: 0
opcode: %x1 means text frame


Not checking:
'sequence' indicating each sent message, there is no verification if I didn't miss any

"""
