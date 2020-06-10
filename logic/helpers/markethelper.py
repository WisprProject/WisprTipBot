import json
import logging
from datetime import datetime

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from logic.common.botusererror import BotUserError
from logic.helpers.configuration import Configuration

global coin_update_time
global coin_data
coin_update_time = None
coin_data = None


def get_fiat_price():
    data = get_coin_data()
    return data[ 'quote' ][ 'USD' ][ 'price' ]


def get_market_cap():
    data = get_coin_data()
    return data[ 'quote' ][ 'USD' ][ 'market_cap' ]


def get_coin_data():
    global coin_update_time
    global coin_data
    now = datetime.now()
    current_time = datetime.timestamp( now )

    if coin_update_time is None or current_time - coin_update_time > Configuration.COINMARKETCAP_CACHE_UPDATE_INTERVAL:
        update_coin_data_cache()

    return coin_data


def update_coin_data_cache():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = { 'symbol': Configuration.COIN_SYMBOL }
    headers = { 'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': Configuration.COINMARKETCAP_API_TOKEN }
    session = Session()
    session.headers.update( headers )

    try:
        global coin_data
        global coin_update_time
        response = session.get( url, params = parameters )
        data = json.loads( response.text )
        if 'error_code' in response.text and data[ 'status' ][ 'error_code' ] == 400:
            raise BotUserError( f'No market info available for {Configuration.COIN_SYMBOL}.' )
        coin_data = data[ 'data' ][ Configuration.COIN_SYMBOL ]
        now = datetime.now()
        coin_update_time = datetime.timestamp( now )

        logging.info( 'Coin data cache updated' )
        logging.info( coin_data )
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logging.error( e )
