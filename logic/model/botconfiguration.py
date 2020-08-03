from typing import List

from logic.common.configuration import Configuration
from logic.model.coinproperties import CoinProperties


class BotConfiguration:
    logging_level: str
    telegram_bot_name: str
    telegram_bot_token: str
    coins: List[ CoinProperties ]
    coinmarketcap_api_token: str
    coinmarketcap_cache_update_interval: int
    chat_activity_time: int

    def __init__( self, configuration: Configuration ):
        self.logging_level = configuration.LOGGING_LEVEL
        self.telegram_bot_name = configuration.TELEGRAM_BOT_NAME
        self.telegram_bot_token = configuration.TELEGRAM_BOT_TOKEN
        self.coins = list( map( CoinProperties, configuration.COINS ) )
        self.coinmarketcap_api_token = configuration.COINMARKETCAP_API_TOKEN
        self.coinmarketcap_cache_update_interval = configuration.COINMARKETCAP_CACHE_UPDATE_INTERVAL
        self.chat_activity_time = configuration.CHAT_ACTIVITY_TIME
        self.request_kwargs = configuration.REQUEST_KWARGS
