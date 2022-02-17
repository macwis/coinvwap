from payload import split_frames


class FakeRecv:
    def __init__(self) -> None:
        self.data = open(  # pylint: disable=consider-using-with
            "src/tests/data/recv.stream_sample", "rb"
        )
        self.carret = 0

    def recv(self, piece_size):
        return self.data.read(piece_size)

    def close(self):
        self.data.close()


def test_split_frames():

    fake_recv = FakeRecv()

    parsed_data = []

    for payload in split_frames(fake_recv.recv, 1024):
        parsed_data.append(payload)

    fake_recv.close()

    # check count
    assert len(parsed_data) == 166
    # check first
    assert parsed_data[0] == {
        "type": "ticker",
        "sequence": 25817411093,
        "product_id": "ETH-USD",
        "price": "3149.35",
        "open_24h": "3140.55",
        "volume_24h": "141795.60378986",
        "low_24h": "3043.41",
        "high_24h": "3190",
        "volume_30d": "6841610.19719532",
        "best_bid": "3149.34",
        "best_ask": "3149.35",
        "side": "buy",
        "time": "2022-02-17T01:29:30.220661Z",
        "trade_id": 224332747,
        "last_size": "0.00275791",
    }
    # check last
    assert parsed_data[-1] == {
        "type": "ticker",
        "sequence": 34196893511,
        "product_id": "BTC-USD",
        "price": "44121.94",
        "open_24h": "44011.44",
        "volume_24h": "9134.04878562",
        "low_24h": "43330.59",
        "high_24h": "44411.06",
        "volume_30d": "539340.34465432",
        "best_bid": "44120.54",
        "best_ask": "44121.94",
        "side": "buy",
        "time": "2022-02-17T01:29:45.108782Z",
        "trade_id": 282258684,
        "last_size": "0.00108252",
    }
