import json

with open( 'config.json', 'r' ) as configFile:
    config = json.load( configFile )


class Configuration:
    REQUEST_KWARGS = config[ 'REQUEST_KWARGS' ]
    LOGGING_LEVEL = config[ 'LOGGING_LEVEL' ][ 'INFO' ]
    TELEGRAM_BOT_TOKEN = config[ 'TELEGRAM_BOT_TOKEN' ]
    TELEGRAM_BOT_NAME = config[ 'TELEGRAM_BOT_NAME' ]
    COIN_SYMBOL = config[ 'COIN_SYMBOL' ]
    COINMARKETCAP_API_TOKEN = config[ 'COINMARKETCAP_API_TOKEN' ]
    COINMARKETCAP_CACHE_UPDATE_INTERVAL = config[ 'COINMARKETCAP_CACHE_UPDATE_INTERVAL' ]
    CLI_LOCATION = config[ 'WALLET_CLI_LOCATION' ]
    CHAT_ACTIVITY_TIME = config[ 'CHAT_ACTIVITY_TIME' ]
