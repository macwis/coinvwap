from coinvwap import Coinvwap

if __name__ == "__main__":
    cvp = Coinvwap(
        url="wss://ws-feed.exchange.coinbase.com/",
        product_ids=["BTC-USD", "ETH-USD", "ETH-BTC"],
        channel="ticker",
        type_field="ticker",
        price_field="price",
        quantity_field="last_size",
    )
    cvp.connect()
    cvp.listen(report_fn=print)
