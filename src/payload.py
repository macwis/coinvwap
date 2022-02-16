import json
import logging


def split_frames(recv_fn, recv_buffer=4096):
    """
    Read websocket data and parse the
    frames into well formed JSON sentences.
    Once the JSON is loaded it yelds the data to
    the main CoinVWAP listen loop for further processing.
    """
    msg = recv_fn(recv_buffer)
    carret = 0
    while carret < len(msg):
        if len(msg) - carret < 4:
            # Payload too short to make sense, let's read more data
            # TODO: test cover various partial-frame cases!
            msg += recv_fn(recv_buffer)
        # fin, rsv1, rsv2, rsv3, opcode
        # expected fin=1, rsv*=0, opcode=0x1 (OPCODE_TEXT)
        if f"{msg[carret]:08b}" == "10000001":
            length = msg[carret + 2] << 8 | msg[carret + 3]
            content = msg[carret + 4 : carret + length + 4]
            try:
                parsed = json.loads(content)
                yield parsed
                carret = carret + 4 + length
            except json.decoder.JSONDecodeError:
                logging.debug("Buffer was short, reading in more ..")
                msg += recv_fn(recv_buffer)
