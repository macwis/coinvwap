import random
import time

from vwap import VWAPStore, VWAPStoreFast


def test_vwap_performance():

    payloads = [
        {
            "type": "match",
            "product_id": "ETH-BTC",
            "price": random.random(),
            "quantity": random.random(),
        }
        for i in range(0, 10 ^ 6)
    ]

    def evaluate(store, payloads):
        start = time.time()
        vwapstore = store(
            product_ids=["ETH-BTC"],
            price_field="price",
            quantity_field="quantity",
            type_field="match",
        )
        for payload in payloads:
            vwapstore.store(payload)
            vwapstore.report()
        report = vwapstore.report()
        end = time.time()
        return (end - start, report)

    exec_time, report = evaluate(VWAPStore, payloads)
    exec_time_fast, report_fast = evaluate(VWAPStoreFast, payloads)
    assert report == report_fast
    # Should be at least 40% faster!
    # e.g. 000.000198 vs. 000.000098
    print(f"{exec_time:010f}", f"{exec_time_fast:010f}")
    assert exec_time * 0.60 > exec_time_fast
