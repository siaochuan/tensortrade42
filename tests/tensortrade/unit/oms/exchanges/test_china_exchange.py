from tensortrade.oms.exchanges.china_exchange import ChinaExchange
from tensortrade.oms.instruments import CNY, SH600519, CSI300, IF
from tensortrade.feed import Stream
from tensortrade.oms.services.execution.simulated import execute_order


def test_china_exchange_defaults():
    ex = ChinaExchange('china', service=execute_order)
    assert hasattr(ex, 'options')
    assert ex.options.commission == 0.001
    assert ex.options.min_trade_price == 0.01


def test_china_exchange_tradable_and_quote_price():
    s1 = Stream.source([10.0, 10.5], dtype='float').rename('CNY-SH600519')
    s2 = Stream.source([3000.0, 3050.0], dtype='float').rename('CNY-IF')

    ex = ChinaExchange('china', service=execute_order)(s1, s2)

    # Make sure streams have values
    s1.run()
    s2.run()

    assert ex.is_pair_tradable(CNY / SH600519)
    assert ex.is_pair_tradable(CNY / IF)

    p = ex.quote_price(CNY / SH600519)
    assert p is not None
