import time
from threading import Thread

from coinvwap import Coinvwap


class SimpleTextBuffer:
    def __init__(self) -> None:
        self.buffer = ""

    def write(self, content, end=""):
        self.buffer += content + end

    def readall(self):
        return self.buffer


def test_integration():
    """
    This is a typical online integration test.
    NOTE: There are different preferences how to run this sort of tests.
          For simplicity I left it here to just run with all the other,
          but good practice is to keep them separated with a different runable.
          (To convert to a proper unittest - an option is to mock the socket stream.)
    """
    buf = SimpleTextBuffer()
    cvp = Coinvwap()
    cvp.connect()
    listen_thread = Thread(target=cvp.listen, kwargs={"report_fn": buf.write})
    listen_thread.start()
    time.sleep(1)
    cvp.disconnect()

    rows = buf.readall().split("\n")
    data = [row.split("\t") for row in rows]

    assert len(data) > 1
    assert data[0][0] in ["BTC-USD", "ETH-USD", "ETH-BTC"]
    assert float(data[0][1]) > 0
    assert data[0][2] == "points:"
    assert int(data[0][3]) > 0
