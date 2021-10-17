import json
import requests

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from api_retry_wrapper import RetryWrapper

class Analyzer:
    """Handles technical analaysis API tools and returns techincal analysis and other information"""
    def __init__(self, config=None, logger=None):
        self.cmc_api_key = config['cmc_api_key']
        self.cmc_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.taapi_api_key = config['taapi_api_key']
        self.taapi_bulk_url = 'https://api.taapi.io/bulk'
        self.logger = logger
        if self.cmc_api_key == '' or self.taapi_api_key == '':
            raise Exception("Missing API keys for technical analysis tools!")
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.cmc_api_key
        }
        self.session = Session()
        self.session.headers.update(headers)

    @RetryWrapper(5, 10)
    def get_cmc_info(self, self.logger):
        data = None
        parameters = {
            'start':'1',
            'limit':'32',
            'convert':'USDT',
            'market_cap_min': 2000000000,
            'volume_24h_min': 35000000
        }
        response = self.session.get(self.cmc_url, params=parameters)
        data = json.loads(response.text)
        if data:
            targets = data['data']
            sortedTargets = sorted(targets, key=lambda k: k['quote']['USDT']['percent_change_7d'], reverse=False)
            return sortedTargets
        else:
             return None

    @RetryWrapper(5, 2)
    def get_1d_tech_info(self, pair, self.logger):
        result = None
        taapiSymbol = pair.split('USDT')[0] + "/" + "USDT"
        parameters = {
            "secret": self.taapi_api_key,
            "construct": {
                "exchange": "binance",
                "symbol": taapiSymbol,
                "interval": "1d",
                "indicators": [
                {
                    # Current Relative Strength Index
                    "id": "thisrsi",
                    "indicator": "rsi"
                },
                {
                    # Current stoch fast
                    "id": "thisstochf",
                    "indicator": "stochf",
                    "optInFastK_Period": 3,
                    "optInFastD_Period": 3
                }
                ]
            }
        }
        # Send POST request and save the response as response object
        response = requests.post(url = self.taapi_bulk_url, json = parameters)
        # Extract data in json format
        result = response.json()
        return result
