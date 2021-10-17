#!/usr/bin/env python3
import time
from binance.client import Client
from binance.exceptions import *
from api_retry_wrapper import RetryWrapper

class Exchanger:
    """Configures and runs the right exchange based on the selected exchange in config"""
    def __init__(self, config=None):
        self.exchange = config['exchange']
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']

        if self.exchange == 'binance':
            binance = Binance(public_key = self.api_key, secret_key = self.api_secret, sync=True)
            self.account = binance.b

        if not self.account:
            raise Exception('Could not connect to the exchange account with provided keys!')

    @RetryWrapper(5, 5)
    def get_all_tickers(self):
        result = None
        tickers = self.account.get_all_tickers()
        result = [item for item in tickers if 'USDT' in item['symbol']]
        return tickers
    
    @RetryWrapper(5, 5)
    def get_tickers(self, pair='BTCUSDT'):
        # Get pair ticker info
        if self.exchange == 'binance':
            tickers = self.account.get_orderbook_tickers()
            # Example Binance {'symbol': 'ETHBTC', 'bidPrice': '0.02706800', 'bidQty': '7.30000000', 'askPrice': '0.02707300', 'askQty': '24.00000000'} # Bid == BUY, ask == SELL
            ticker = next((x for x in tickers if x["symbol"] == pair), None)
            if ticker:
                return({'buy_price': float(ticker["bidPrice"]), 'sell_price': float(ticker["askPrice"])})
            else:
                return None

    @RetryWrapper(5, 5)
    def get_balance(self, coin):
        # Get account balances
        if self.exchange == 'binance':
            currency_balance = self.account.get_asset_balance(asset=coin) or 0.0
            if currency_balance == 0.0:
                base_currency_available = 0.0
            else:
                base_currency_available = float(currency_balance["free"])
            return float(currency_balance)

    @RetryWrapper(5, 5)
    def order_market_buy(self, pair, quantity=0.0):
        if self.exchange == 'binance':
            self.account.order_market_buy(symbol=pair, quantity=quantity)

    @RetryWrapper(5, 5)
    def order_market_sell(self, pair, quantity=0.0):
        if self.exchange == 'binance':
            self.account.order_market_sell(symbol=pair, quantity=quantity)

# This wrapper solves time-offset inconsistencies between local-PC time and Binance server time
class Binance:
    def __init__(self, public_key='', secret_key='', sync=False):
        self.time_offset = 0
        self.b = Client(public_key, secret_key)
        if sync:
            self.time_offset = self._get_time_offset()
    def _get_time_offset(self):
        res = self.b.get_server_time()
        return res['serverTime'] - int(time.time() * 1000)
    def synced(self, fn_name, **args):
        args['timestamp'] = int(time.time() - self.time_offset)
