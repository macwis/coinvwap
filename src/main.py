from coinvwap import Coinvwap


if __name__ == "__main__":
    cvp = Coinvwap(
        "wss://ws-feed.exchange.coinbase.com/",
        ["BTC-USD", "ETH-USD", "ETH-BTC"],
    )
    cvp.connect()
    # TODO: Listen can be wrapped in a thread or separate process
    #       no to block the main thread and perform watchdog operations.
    cvp.listen()
