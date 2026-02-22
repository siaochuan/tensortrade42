import sys
import os

# 确保路径正确添加
project_root = "/Users/rc/laifu/pluck"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加tensortrade的子路径
tensortrade_path = os.path.join(project_root, "tensortrade")
if tensortrade_path not in sys.path:
    sys.path.insert(0, tensortrade_path)

# 验证路径是否存在
print(f"路径存在: {os.path.exists(project_root)}")
print(f"TensorTrade路径存在: {os.path.exists(tensortrade_path)}")

# 清除可能存在的缓存
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('tensortrade')]
for mod in modules_to_remove:
    del sys.modules[mod]

# 尝试导入TensorTrade
try:
    import tensortrade.env.default as default
    print("成功导入 tensortrade.env.default")
except ImportError as e:
    print(f"导入失败: {e}")
    
    # 尝试不同的导入路径
    try:
        from tensortrade.env import default
        print("成功导入 tensortrade.env.default (alternative)")
    except ImportError as e2:
        print(f"替代导入也失败: {e2}")
        
        # 列出tensortrade目录的实际内容
        import os
        print(f"tensortrade目录内容: {os.listdir(tensortrade_path)}")

# 导入其他必要的模块
from tensortrade.feed.core import Stream, DataFeed
from tensortrade.data.cdd import CryptoDataDownload

# 原始ledger_example代码开始
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from tensortrade.env.default import actions
from tensortrade.env.default import rewards
from tensortrade.env.default import observers
from tensortrade.env.default import stoppers
from tensortrade.env.default import informers

# 使用正确的导入路径
from tensortrade.oms.exchanges import Exchange
from tensortrade.oms.instruments import USD, ETH, Instrument
from tensortrade.oms.instruments import Quantity
from tensortrade.oms.wallets import Wallet, Portfolio
from tensortrade.oms.orders import Order
from tensortrade.oms.services.execution.simulated import execute_order

np.warnings = warnings
pd.options.mode.chained_assignment = None

# 创建交易对
ETH_USD = ETH / USD

# 创建模拟交易所服务函数
def create_simulated_exchange_service():
    def service_func(order: 'Order',
                     base_wallet: 'Wallet',
                     quote_wallet: 'Wallet',
                     current_price: float,
                     options: 'ExchangeOptions',
                     clock: 'Clock') -> 'Trade':
        return execute_order(
            order=order,
            base_wallet=base_wallet,
            quote_wallet=quote_wallet,
            current_price=current_price,
            options=options,
            clock=clock
        )
    return service_func

# 创建模拟交易所
exchange = Exchange("coinbase", service=create_simulated_exchange_service())

# 创建钱包和投资组合
wallet_eth = Wallet(exchange, Quantity(ETH, 10))
wallet_usd = Wallet(exchange, Quantity(USD, 10000))

portfolio = Portfolio(USD, [wallet_eth, wallet_usd])

print("TensorTrade环境已成功创建！")