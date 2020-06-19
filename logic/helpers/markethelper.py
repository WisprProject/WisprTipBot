import json
import logging
from datetime import datetime

from requests import Session

from logic.common.botusererror import BotUserError
from logic.common.configuration import Configuration

logger = logging.getLogger( __name__ )

global coin_data
coin_data = { }


def get_fiat_price( ticker ):
    data = get_coin_data( ticker )
    return data[ 'quote' ][ 'USD' ][ 'price' ]


def get_market_cap( ticker ):
    data = get_coin_data( ticker )
    return data[ 'quote' ][ 'USD' ][ 'market_cap' ]


def get_coin_data( ticker ):
    global coin_data

    now = datetime.now()
    current_time = datetime.timestamp( now )

    if ticker not in coin_data or current_time - coin_data[ ticker ][ "update_time" ] > Configuration.COINMARKETCAP_CACHE_UPDATE_INTERVAL:
        update_coin_data_cache( ticker, current_time )

    return coin_data[ ticker ][ 'data' ]


def update_coin_data_cache( ticker, current_time ):
    global coin_data

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = { 'symbol': ticker }
    headers = { 'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': Configuration.COINMARKETCAP_API_TOKEN }
    session = Session()
    session.headers.update( headers )

    global coin_data
    response = session.get( url, params = parameters )
    data = json.loads( response.text )

    if 'error_code' in response.text and data[ 'status' ][ 'error_code' ] == 400:
        raise BotUserError( f'No market info available for {ticker}.' )

    if ticker not in coin_data:
        coin_data.update( { ticker: { 'data': data[ 'data' ][ ticker ], "update_time": current_time } } )
    else:
        coin_data[ ticker ].update( { 'data': data[ 'data' ][ ticker ], "update_time": current_time } )

    logger.info( 'Coin market data cache updated.' )
    logger.debug( coin_data )
