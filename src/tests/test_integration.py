import time
from threading import Thread

from coinvwap import Coinvwap


def test_integration():
    """
    This is a typical online integration test.
    NOTE: There are different preferences how to run this sort of tests.
          For simplicity I left it here to just run with all the other,
          but good practice is to keep them separated with a different runable.
          (To convert to a proper unittest - an option is to mock the socket stream.)
    """
    cvp = Coinvwap()
    cvp.connect()
    listen_thread = Thread(target=cvp.listen)
    listen_thread.start()
    time.sleep(2)
    cvp.disconnect()
