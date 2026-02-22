from tensortrade.oms.exchanges.exchange import Exchange, ExchangeOptions


class ChinaExchange(Exchange):
    """An Exchange subclass with sensible defaults for Chinese markets.

    This minimal subclass currently sets default commission and price/size
    ranges suitable for equities and index futures denominated in CNY.
    """

    def __init__(self, name: str, service, options: ExchangeOptions = None):
        default_opts = ExchangeOptions(
            commission=0.001,
            min_trade_size=1e-2,
            max_trade_size=1e6,
            min_trade_price=0.01,
            max_trade_price=1e8,
            is_live=False
        )
        super().__init__(name=name, service=service, options=options or default_opts)
