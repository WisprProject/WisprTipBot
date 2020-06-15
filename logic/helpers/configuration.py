import json

with open( 'config.json', 'r' ) as configFile:
    config = json.load( configFile )


class Configuration:
    REQUEST_KWARGS = config[ 'REQUEST_KWARGS' ]
    LOGGING_LEVEL = config[ 'LOGGING_LEVEL' ]
    TELEGRAM_BOT_TOKEN = config[ 'TELEGRAM_BOT_TOKEN' ]
    TELEGRAM_BOT_NAME = config[ 'TELEGRAM_BOT_NAME' ]
    COIN_TICKER = config[ 'COIN_TICKER' ]
    COIN_NAME = config[ 'COIN_NAME' ]
    COINMARKETCAP_API_TOKEN = config[ 'COINMARKETCAP_API_TOKEN' ]
    COINMARKETCAP_CACHE_UPDATE_INTERVAL = config[ 'COINMARKETCAP_CACHE_UPDATE_INTERVAL' ]
    CHAT_ACTIVITY_TIME = config[ 'CHAT_ACTIVITY_TIME' ]
    RPC_CONFIGURATION = config[ 'RPC_CONFIGURATION' ]
