from dataclasses import dataclass, field
from typing import Dict, Optional

# Minimal spot & futures utilities for OMS (standalone; no external deps).

@dataclass
class Position:
    qty: float = 0.0
    avg_cost: float = 0.0

    def apply_trade(self, qty: float, price: float) -> float:
        realized = 0.0
        if qty == 0.0:
            return 0.0
        if self.qty == 0 or (self.qty > 0 and qty > 0) or (self.qty < 0 and qty < 0):
            new_qty = self.qty + qty
            if new_qty != 0:
                self.avg_cost = (self.qty * self.avg_cost + qty * price) / new_qty
            self.qty = new_qty
            return 0.0
        if self.qty > 0 and qty < 0:
            close_qty = min(self.qty, -qty)
            realized += (price - self.avg_cost) * close_qty
            self.qty -= close_qty
            qty += close_qty
            if self.qty == 0:
                self.avg_cost = 0.0
        elif self.qty < 0 and qty > 0:
            close_qty = min(-self.qty, qty)
            realized += (self.avg_cost - price) * close_qty
            self.qty += close_qty
            qty -= close_qty
            if self.qty == 0:
                self.avg_cost = 0.0
        if qty != 0:
            self.avg_cost = price
            self.qty += qty
        return realized

@dataclass
class FuturesPosition:
    qty: float = 0.0
    multiplier: float = 1.0
    prev_settlement: float = 0.0
    def change(self, dq: float) -> None:
        self.qty += dq

@dataclass
class Wallet:
    base_currency: str
    cash: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)
    realized_pnl: float = 0.0
    futures_positions: Dict[str, FuturesPosition] = field(default_factory=dict)
    realized_pnl_futures: float = 0.0
    def position(self, symbol: str) -> Position:
        pos = self.positions.get(symbol)
        if pos is None:
            pos = Position()
            self.positions[symbol] = pos
        return pos
    def futures(self, symbol: str, multiplier: float, pre_settlement: float) -> FuturesPosition:
        fp = self.futures_positions.get(symbol)
        if fp is None:
            fp = FuturesPosition(qty=0.0, multiplier=multiplier, prev_settlement=pre_settlement)
            self.futures_positions[symbol] = fp
        else:
            fp.multiplier = multiplier
            fp.prev_settlement = pre_settlement
        return fp

class Exchange:
    def __init__(self, fee_rate: float = 0.0) -> None:
        self.fee_rate = float(fee_rate)
        self._marks: Dict[str, float] = {}
    def set_mark(self, symbol: str, price: float) -> None:
        self._marks[symbol] = float(price)
    def mark(self, symbol: str, fallback: Optional[float] = None) -> Optional[float]:
        return self._marks.get(symbol, fallback)
    def execute(self, wallet: Wallet, symbol: str, qty: float, price: float) -> None:
        qty = float(qty)
        price = float(price)
        fee = abs(qty) * price * self.fee_rate
        realized = wallet.position(symbol).apply_trade(qty, price)
        wallet.realized_pnl += realized
        wallet.cash += -qty * price
        wallet.cash -= fee
    def execute_futures(self, wallet: Wallet, symbol: str, qty: float, price: float, multiplier: float) -> None:
        qty = float(qty)
        price = float(price)
        multiplier = float(multiplier)
        fee = abs(qty) * price * self.fee_rate
        wallet.cash -= fee
        fp = wallet.futures_positions.get(symbol)
        if fp is None:
            fp = FuturesPosition(qty=0.0, multiplier=multiplier, prev_settlement=price)
            wallet.futures_positions[symbol] = fp
        else:
            fp.multiplier = multiplier
        fp.change(qty)

class SettlementEngine:
    def __init__(self, wallet: Wallet, exchange: Exchange) -> None:
        self.wallet = wallet
        self.ex = exchange
    def _spot_mark(self, symbol: str, default: float = 0.0) -> float:
        m = self.ex.mark(symbol)
        return float(m if m is not None else default)
    def _fut_mark(self, symbol: str, prev_settlement: float) -> float:
        m = self.ex.mark(symbol, fallback=prev_settlement)
        return float(m)
    def snapshot(self, margin_rate: Optional[float] = None) -> Dict[str, float]:
        market_value = 0.0
        unrealized = 0.0
        for sym, pos in self.wallet.positions.items():
            mark = self._spot_mark(sym, default=0.0)
            market_value += pos.qty * mark
            unrealized += (mark - pos.avg_cost) * pos.qty
        unrealized_f = 0.0
        margin_locked = 0.0
        for sym, fp in self.wallet.futures_positions.items():
            mark = self._fut_mark(sym, fp.prev_settlement)
            unrealized_f += (mark - fp.prev_settlement) * fp.qty * fp.multiplier
            if margin_rate is not None:
                margin_locked += abs(fp.qty) * mark * fp.multiplier * float(margin_rate)
        equity = self.wallet.cash + market_value + unrealized_f
        out = {
            'cash': self.wallet.cash,
            'market_value': market_value,
            'equity': equity,
            'realized_pnl': self.wallet.realized_pnl,
            'unrealized_pnl': unrealized,
            'realized_pnl_futures': self.wallet.realized_pnl_futures,
            'unrealized_pnl_futures': unrealized_f,
        }
        if margin_rate is not None:
            out['margin_locked'] = margin_locked
        return out
    def settle_futures(self, settlement_prices: Dict[str, float], margin_rate: Optional[float] = None) -> Dict[str, float]:
        realized_today = 0.0
        for sym, settle in settlement_prices.items():
            if sym not in self.wallet.futures_positions:
                self.ex.set_mark(sym, float(settle))
                continue
            fp = self.wallet.futures_positions[sym]
            settle = float(settle)
            var = (settle - fp.prev_settlement) * fp.qty * fp.multiplier
            realized_today += var
            self.wallet.cash += var
            self.wallet.realized_pnl_futures += var
            fp.prev_settlement = settle
            self.ex.set_mark(sym, settle)
        snap = self.snapshot(margin_rate=margin_rate)
        snap['realized_today_futures'] = realized_today
        return snap
