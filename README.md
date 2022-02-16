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

---

## Some meaningless random notes

Framing protocol specs: https://datatracker.ietf.org/doc/html/rfc6455#section-5.2

```python
raw_sub = b'\x81\xfe\x00\x87\x16\x98\xa4\xe7m\xba\xd0\x9ef\xfd\x86\xdd6\xba\xd7\x92t\xeb\xc7\x95\x7f\xfa\xc1\xc5:\xb8\x86\x97d\xf7\xc0\x92u\xec\xfb\x8er\xeb\x86\xdd6\xc3\x86\xa5B\xdb\x89\xb2E\xdc\x86\xba:\xb8\x86\x84~\xf9\xca\x89s\xf4\xd7\xc5,\xb8\xff\xc5~\xfd\xc5\x95b\xfa\xc1\x86b\xba\x88\xc7m\xba\xca\x86{\xfd\x86\xdd6\xba\xd0\x8eu\xf3\xc1\x954\xb4\x84\xc5f\xea\xcb\x83c\xfb\xd0\xb8\x7f\xfc\xd7\xc5,\xb8\xff\xc5T\xcc\xe7\xcaC\xcb\xe0\xc5:\xb8\x86\xa5B\xdb\x89\xa0T\xc8\x86\xbak\xc5\xd9'
print("{:03b}".format(raw_sub[0]))
# gives: '10000001'
```

```
fin: 1
rsv1: 0
rsv2: 0
rsv3: 0
opcode: %x1 means text frame
```

Not checking:
'sequence' indicating each sent message, there is no verification if I didn't miss any
''
