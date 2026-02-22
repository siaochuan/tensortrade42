import importlib.util
from pathlib import Path

# Load the module directly by file path to avoid importing full tensortrade pkg
_settle_path = Path(__file__).resolve().parents[2] / 'tensortrade' / 'oms' / 'futures' / 'settlement.py'
spec = importlib.util.spec_from_file_location('tt_oms_futures_settlement', _settle_path)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)  # type: ignore
Exchange = mod.Exchange
Wallet = mod.Wallet
SettlementEngine = mod.SettlementEngine

def approx(a, b, eps=1e-9):
    return abs(a - b) <= eps

def test_spot_and_mark():
    ex = Exchange(fee_rate=0.001)
    w = Wallet(base_currency='CNY', cash=100000.0)
    ex.execute(w, '000001.SSE', qty=100.0, price=10.0)
    assert approx(w.cash, 98999.0)
    ex.set_mark('000001.SSE', 11.0)
    snap = SettlementEngine(w, ex).snapshot()
    assert approx(snap['market_value'], 1100.0)
    assert approx(snap['unrealized_pnl'], 100.0)
    assert approx(snap['equity'], 98999.0 + 1100.0)

def test_partial_sell_realize():
    ex = Exchange(fee_rate=0.001)
    w = Wallet(base_currency='CNY', cash=100000.0)
    ex.execute(w, '000001.SSE', qty=100.0, price=10.0)
    ex.set_mark('000001.SSE', 11.0)
    ex.execute(w, '000001.SSE', qty=-50.0, price=11.0)
    assert approx(w.realized_pnl, 50.0)
    assert approx(w.cash, 99548.45)
    ex.set_mark('000001.SSE', 11.5)
    snap = SettlementEngine(w, ex).snapshot()
    assert approx(snap['unrealized_pnl'], (11.5 - 10.0)*50.0)

def test_futures_intraday_and_settle_long():
    ex = Exchange(fee_rate=0.0)
    w = Wallet(base_currency='CNY', cash=100000.0)
    w.futures('IF2403', multiplier=300.0, pre_settlement=4000.0)
    ex.execute_futures(w, 'IF2403', qty=1.0, price=4010.0, multiplier=300.0)
    ex.set_mark('IF2403', 4030.0)
    snap = SettlementEngine(w, ex).snapshot(margin_rate=0.1)
    assert approx(snap['unrealized_pnl_futures'], 9000.0)
    assert approx(snap['margin_locked'], 4030.0*300.0*0.1)
    snap2 = SettlementEngine(w, ex).settle_futures({'IF2403': 4050.0}, margin_rate=0.1)
    assert approx(snap2['realized_today_futures'], 15000.0)
    assert approx(snap2['unrealized_pnl_futures'], 0.0)
    assert approx(snap2['cash'], 115000.0)

def test_futures_settle_short_gain():
    ex = Exchange(fee_rate=0.0)
    w = Wallet(base_currency='CNY', cash=50000.0)
    w.futures('IF2404', multiplier=200.0, pre_settlement=5000.0)
    ex.execute_futures(w, 'IF2404', qty=-2.0, price=4990.0, multiplier=200.0)
    snap = SettlementEngine(w, ex).settle_futures({'IF2404': 4950.0}, margin_rate=0.12)
    assert approx(snap['realized_today_futures'], 20000.0)
    assert approx(snap['cash'], 70000.0)
