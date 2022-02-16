"""
The code below has been heavily borrowed from:
https://github.com/websocket-client/websocket-client/blob/e49e0e88a37c2ba0765eb67522f7ac809fe40709/websocket/_abnf.py#L1

_abnf.py
websocket - WebSocket client library for Python

Copyright 2022 engn33r

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import array
import os
import struct
import sys

native_byteorder = sys.byteorder


def _mask(mask_value, data_value):
    datalen = len(data_value)
    data_value = int.from_bytes(data_value, native_byteorder)
    mask_value = int.from_bytes(
        mask_value * (datalen // 4) + mask_value[: datalen % 4], native_byteorder
    )
    return (data_value ^ mask_value).to_bytes(datalen, native_byteorder)


class ABNF:
    """
    ABNF frame class.
    See http://tools.ietf.org/html/rfc5234
    and http://tools.ietf.org/html/rfc6455#section-5.2
    """

    # operation code values.
    OPCODE_CONT = 0x0
    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xA

    # available operation code value tuple
    OPCODES = (
        OPCODE_CONT,
        OPCODE_TEXT,
        OPCODE_BINARY,
        OPCODE_CLOSE,
        OPCODE_PING,
        OPCODE_PONG,
    )

    # opcode human readable string
    OPCODE_MAP = {
        OPCODE_CONT: "cont",
        OPCODE_TEXT: "text",
        OPCODE_BINARY: "binary",
        OPCODE_CLOSE: "close",
        OPCODE_PING: "ping",
        OPCODE_PONG: "pong",
    }

    # data length threshold.
    LENGTH_7 = 0x7E
    LENGTH_16 = 1 << 16
    LENGTH_63 = 1 << 63

    def __init__(
        self, fin=0, rsv1=0, rsv2=0, rsv3=0, opcode=OPCODE_TEXT, mask=1, data=""
    ):
        """
        Constructor for ABNF. Please check RFC for arguments.
        """
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.mask = mask
        if data is None:
            data = ""
        self.data = data
        self.get_mask_key = os.urandom

    def __str__(self):
        return (
            "fin="
            + str(self.fin)
            + " opcode="
            + str(self.opcode)
            + " data="
            + str(self.data)
        )

    @staticmethod
    def create_frame(data, opcode, fin=1):
        """
        Create frame to send text, binary and other data.
        Parameters
        ----------
        data: <type>
            data to send. This is string value(byte array).
            If opcode is OPCODE_TEXT and this value is unicode,
            data value is converted into unicode string, automatically.
        opcode: <type>
            operation code. please see OPCODE_XXX.
        fin: <type>
            fin flag. if set to 0, create continue fragmentation.
        """
        if opcode == ABNF.OPCODE_TEXT and isinstance(data, str):
            data = data.encode("utf-8")
        # mask must be set if send data from client
        return ABNF(fin, 0, 0, 0, opcode, 1, data)

    def format(self):
        """
        Format this object to string(byte array) to send data to server.
        """
        if any(x not in (0, 1) for x in [self.fin, self.rsv1, self.rsv2, self.rsv3]):
            raise ValueError("not 0 or 1")
        if self.opcode not in ABNF.OPCODES:
            raise ValueError("Invalid OPCODE")
        length = len(self.data)
        if length >= ABNF.LENGTH_63:
            raise ValueError("data is too long")

        # Tip:
        # "{:03b}".format(fin << 7 | 0 << 6 | 0 << 5 | 0 << 4 | 0x1)
        # '10000001'
        frame_header = chr(
            self.fin << 7
            | self.rsv1 << 6
            | self.rsv2 << 5
            | self.rsv3 << 4
            | self.opcode
        ).encode("latin-1")
        if length < ABNF.LENGTH_7:
            frame_header += chr(self.mask << 7 | length).encode("latin-1")
        elif length < ABNF.LENGTH_16:
            frame_header += chr(self.mask << 7 | 0x7E).encode("latin-1")
            frame_header += struct.pack(
                "!H", length
            )  # ! network (= big-endian), H unsigned short
        else:
            frame_header += chr(self.mask << 7 | 0x7F).encode("latin-1")
            frame_header += struct.pack(
                "!Q", length
            )  # ! network (= big-endian), Q unsigned long long

        if not self.mask:
            return frame_header + self.data
        else:
            mask_key = self.get_mask_key(4)
            return frame_header + self._get_masked(mask_key)

    def _get_masked(self, mask_key):
        s = ABNF.mask(mask_key, self.data)

        if isinstance(mask_key, str):
            mask_key = mask_key.encode("utf-8")

        return mask_key + s

    @staticmethod
    def mask(mask_key, data):
        """
        Mask or unmask data. Just do xor for each byte
        Parameters
        ----------
        mask_key: <type>
            4 byte string.
        data: <type>
            data to mask/unmask.
        """
        if data is None:
            data = ""

        if isinstance(mask_key, str):
            mask_key = mask_key.encode("latin-1")

        if isinstance(data, str):
            data = data.encode("latin-1")

        return _mask(array.array("B", mask_key), array.array("B", data))
