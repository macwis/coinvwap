from vwap import VWAPStore


def test_vwap_store():
    payloads = [
        {
            "type": "match",
            "product_id": "ETH-BTC",
            "price": 0.05478,
            "quantity": 0.072342,
        },
        {
            "type": "match",
            "product_id": "ETH-BTC",
            "price": 0.04478,
            "quantity": 0.042342,
        },
        {
            "type": "match",
            "product_id": "ETH-BTC",
            "price": 0.03478,
            "quantity": 0.042342,
        },
    ]

    store = VWAPStore(
        product_ids=["BTC-USD", "ETH-USD", "ETH-BTC"],
        price_field="price",
        quantity_field="quantity",
        type_field="match",
    )
    for payload in payloads:
        store.store(payload)

    assert (
        store.report()
        == "BTC-USD\t000.000000\nETH-USD\t000.000000\nETH-BTC\t000.046691\n"
    )
