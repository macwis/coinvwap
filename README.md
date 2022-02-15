# coinvwap

## Intro

Coinvwap retrieves a data feed from the coinbase websocket and subscribe to the matches channel.

It pulls data for the following three trading pairs:

- BTC-USD
- ETH-USD
- ETH-BTC

It calculates the [VWAP](https://en.wikipedia.org/wiki/Volume-weighted_average_price)
per trading pair using a sliding window of 200 data points.
Meaning, when a new data point arrives through the websocket feed the oldest data
point will fall off and the new one will be added such that no more than 200 data
points are included in the calculation.

- The first 200 updates will have less than 200 data points included.
- Stream the resulting VWAP values on each websocket update.
- Prints to stdout.

## Design

Coinvwap is written in pure Python without any dependencies, although
to speed up development it contains two classes borrowed from [websocket-client library](),
precisely `ABNF` and `Headers` class.

During development close follow was kept with:

- [RFC6455, especially #section-5.2](https://datatracker.ietf.org/doc/html/rfc6455#section-5.2)
- [RFC5234](https://datatracker.ietf.org/doc/html/rfc5234)

## Development

Requirements:

- Python >=3.8
- [Poetry](https://python-poetry.org/docs/#installation)

Running:

1. For dependencies: `poetry install`
2. For tests: `poetry run ./scripts/run_tests.sh`
3. For build: `poetry run ./scripts/run_build.sh`
4. For use: `poetry run ./scripts/run_local.sh`
