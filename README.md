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
to speed up development it contains two classes borrowed from [websocket-client library](https://github.com/websocket-client/websocket-client),
precisely `ABNF` and `Headers` classes.

During development close follow was kept with:

- [RFC6455, especially #section-5.2](https://datatracker.ietf.org/doc/html/rfc6455#section-5.2)
- [RFC5234](https://datatracker.ietf.org/doc/html/rfc5234)

## Development

Requirements:

- Python >=3.8
- [Poetry](https://python-poetry.org/docs/#installation)

Running:

0. For quick run: `poetry run python src/main.py`

1. For dependencies: `poetry install`

2. For tests: `poetry run ./scripts/run_tests.sh`

3. For build: `poetry build`

---

## Customization

In case of a need to change channel or fields which are read from the
websocket stream there is a wide range of arguments available through
the main object:

```python
cvp = Coinvwap(
    url="wss://ws-feed.exchange.coinbase.com/",
    product_ids=["BTC-USD", "ETH-USD", "ETH-BTC"],
    channel="ticker",
    type_field="ticker"
    price_field="price",
    quantity_field="last_size",
)
```

The code has been tested for a limited combinations of these.
All were not thoroughly tested, so reach out if you run into problems.

---

## Notes / Justifications

### "you may not use any external libraries"

I took "you may not use any external libraries" in the description very-very seriously. The question came just when I run into binary wrapping and then parsing of frames
[rfc6455#section-5.2](https://datatracker.ietf.org/doc/html/rfc6455#section-5.2).

I though I will send a question and make sure this is not an overkill. I even suspected that it might be a part of the task - ability to byte-stream processing based on RFC specs.

The end game is - I have done this in pure python without any websocket library.

### Ambiguity of the proper data use

It wasn't clear on where to get 'quantity' exactly, there is no
field of this name on any of the channels.

Eric suggested to use channel "match" which websocket reports
as unknown. Maybe it requires an account ..

According to the docs: "The ticker channel provides real-time
price updates every time a match happens.
It batches updates in case of cascading matches,
greatly reducing bandwidth requirements."

It seems like the same functionality as `ticker` offers with less bandwidth.
There is no `quantity`, so I used `last_size` which seemed closest.
Anyway, I used what I used - constructor arguments below allow
to customize the subscription.

**FIXME: User fields selected - to be verified, by the code reviewer.**

### Thread wrapping and watchdog

Listener can be wrapped in a thread or separate process
(like I did with the tests/test_integration.py).
This can be done mainly not to block the main thread,
use the output stream as a base for websocket server,
perform watchdog operations or else.

Ofc watchdog operation can be also handled on the OS level.

### Output piping

To pipe the output the report_fn can be passed.

```python
# ...
cvp.connect()
cvp.listen(report_fn=print)
```

### Websocket protocol

My websocket protocol client implementation is very shallow,
the code will not handle too many variations, but it works for Coinbase case!

I did what I could considering the limited time available and "no external libraries" restriction.

Framing protocol specs: https://datatracker.ietf.org/doc/html/rfc6455#section-5.2

Just for a little explanation of what's going on, a subscription frame request example:

```python
raw_sub = b'\x81\xfe\x00\x87\x16\x98\xa4\xe7m\xba\xd0\x9ef\xfd\x86\xdd6\xba\xd7\x92t\xeb\xc7\x95\x7f\xfa\xc1\xc5:\xb8\x86\x97d\xf7\xc0\x92u\xec\xfb\x8er\xeb\x86\xdd6\xc3\x86\xa5B\xdb\x89\xb2E\xdc\x86\xba:\xb8\x86\x84~\xf9\xca\x89s\xf4\xd7\xc5,\xb8\xff\xc5~\xfd\xc5\x95b\xfa\xc1\x86b\xba\x88\xc7m\xba\xca\x86{\xfd\x86\xdd6\xba\xd0\x8eu\xf3\xc1\x954\xb4\x84\xc5f\xea\xcb\x83c\xfb\xd0\xb8\x7f\xfc\xd7\xc5,\xb8\xff\xc5T\xcc\xe7\xcaC\xcb\xe0\xc5:\xb8\x86\xa5B\xdb\x89\xa0T\xc8\x86\xbak\xc5\xd9'
print("{:03b}".format(raw_sub[0]))
# gives: '10000001'
```

Based on the binary websocket frame model:
```
fin: 1
rsv1: 0
rsv2: 0
rsv3: 0
opcode: 1 = %x1 means text frame
mask
length
```

To avoid covering a lot of cases I focused on the type of responses from Coinbase.

Noted that they all come unmasked and within a certain length limits, so I dropped support for diverted variations and focused completely on this case.

Other coinbase websocket protocol specifics - not checking:
- masking
- sequence count indicating each sent message, there is no verification if I didn't miss any (no account has been used, so free feed is not complete anyway)
- frame lengths above LENGTH_63
