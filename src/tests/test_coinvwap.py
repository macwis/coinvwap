from coinvwap import Coinvwap


def test_coinvwap_init():
    cvp = Coinvwap()
    init_report = cvp.vwap.report()
    assert (
        init_report
        == """BTC-USD\t000.000000\nETH-USD\t000.000000\nETH-BTC\t000.000000\n"""
    )
