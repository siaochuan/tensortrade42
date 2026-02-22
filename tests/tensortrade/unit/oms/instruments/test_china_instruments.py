import pytest

from tensortrade.oms.instruments import CNY, SH600519, SZ000001, CSI300, IF
from tensortrade.oms.instruments import Instrument
from tensortrade.oms.exchanges import Exchange
from tensortrade.feed import Stream


def test_china_instruments_defined():
    # Basic existence and attributes
    assert isinstance(CNY, Instrument)
    assert CNY.symbol == 'CNY'
    assert CNY.precision == 2

    assert SH600519.symbol.startswith('SH')
    assert SZ000001.symbol.startswith('SZ')
    assert CSI300.symbol == 'CSI300'
    assert IF.symbol == 'IF'


def test_exchange_tradable_with_china_streams():
    # Create simple price streams and attach them to a China exchange
    s1 = Stream.source([100.0, 101.5, 102.3], dtype="float").rename("CNY-SH600519")
    s2 = Stream.source([3000.0, 3050.0, 3100.0], dtype="float").rename("CNY-CSI300")

    ex = Exchange("china", service=lambda **k: None)(s1, s2)

    # Pair naming follows the 'base/quote' convention used in streams (e.g., "CNY-SH600519")
    assert ex.is_pair_tradable(CNY / SH600519)
    assert ex.is_pair_tradable(CNY / CSI300)

    # Run streams once so they have a current value before querying price
    s1.run()
    s2.run()

    # quote_price should return a Decimal and be quantized to base precision
    p = ex.quote_price(CNY / SH600519)
    assert p is not None

