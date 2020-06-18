import decimal
import logging

from db import database, statements
from logic.activitytracker import ActivityTracker
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.common.configuration import Configuration
from logic.helpers import commonhelper, markethelper
from logic.helpers.decimalhelper import round_down

logger = logging.getLogger( __name__ )


def commands( update, coin_properties ):
    return messages.commands( coin_properties[ 'TICKER' ].lower() )


def help( update, coin_properties ):
    return messages.help( coin_properties[ 'TICKER' ].lower() )


def deposit( update, coin_properties ):
    try:
        user = commonhelper.get_username( update )
        deposit_address = clientcommandprocessor.run_client_command( coin_properties[ 'RPC_CONFIGURATION' ], 'getaccountaddress', None, user )
        return f'@{user}, Your depositing address is: {deposit_address}'
    except BotUserError as e:
        logger.info( e )
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def tip( update, coin_properties ):
    ticker = coin_properties[ 'TICKER' ]
    arguments = update.message.text.split( ' ' )
    try:
        if len( arguments ) < 3:
            raise BotUserError( messages.tip_error( ticker.lower() ) )

        user = commonhelper.get_username( update )
        target_user = arguments[ 1 ]
        amount = arguments[ 2 ]

        if '@' not in target_user:
            raise BotUserError( f'That user ´{target_user}´ is not applicable.' )

        target_user = target_user[ 1: ]
        user_balance, wallet_balance = commonhelper.get_user_balance( user, coin_properties )
        amount = commonhelper.get_validated_amount( amount, user, user_balance )

        commonhelper.move_to_main( coin_properties, user, wallet_balance )

        if target_user == user:
            raise BotUserError( 'You can not tip Yourself.' )

        users_balance_changes = [ (user, ticker, str( -amount )),
                                  (target_user, ticker, str( amount )) ]

        connection = database.create_connection()

        with connection:
            database.execute_query( connection, statements.INSERT_USER, (target_user,) )
            database.execute_many( connection, statements.UPDATE_USER_BALANCE, users_balance_changes )

            return f'@{user} tipped @{target_user} of {amount} {ticker}'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def balance( update, coin_properties ):
    ticker = coin_properties[ 'TICKER' ]
    try:
        user = commonhelper.get_username( update )
        fiat_price = markethelper.get_fiat_price( ticker )
        total_balance, wallet_balance = commonhelper.get_user_balance( user, coin_properties )
        total_balance = round_down( total_balance, 8 )
        fiat_balance = total_balance * decimal.Decimal( fiat_price )
        fiat_balance = round_down( fiat_balance, 2 )

        if total_balance == 0:
            message = f'@{user}, Your current balance is empty.'
        else:
            message = f'@{user}, Your current balance is: {total_balance} {ticker}'

        if fiat_balance != 0:
            message += f' ≈  $ {fiat_balance:.2f}'

        commonhelper.move_to_main( coin_properties, user, wallet_balance )

        return message

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def withdraw( update, coin_properties ):
    ticker = coin_properties[ 'TICKER' ]
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 3:
            raise BotUserError( messages.withdraw_error( ticker.lower() ) )

        address = arguments[ 1 ]
        address = commonhelper.get_validated_address( address, coin_properties )
        amount = arguments[ 2 ]
        total_balance, wallet_balance = commonhelper.get_user_balance( user, coin_properties )
        amount = commonhelper.get_validated_amount( amount, user, total_balance )

        commonhelper.move_to_main( coin_properties, user, wallet_balance )
        clientcommandprocessor.run_client_command( 'sendtoaddress', None, address, amount )

        try:
            connection = database.create_connection()
            with connection:
                database.execute_query( connection, statements.UPDATE_USER_BALANCE, (user, ticker, str( -amount ),) )
        except Exception as e:
            logger.error( e )
            return messages.GENERIC_ERROR

        return f'@{user} has successfully withdrawn to address: {address} of {amount} {ticker}.'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def market( update, coin_properties ):
    ticker = coin_properties[ 'TICKER' ]
    try:
        fiat_price = markethelper.get_fiat_price( ticker )
        market_cap = markethelper.get_market_cap( ticker )
        fiat_price = round( fiat_price, 4 )
        market_cap = round( market_cap, 2 )

        return f'The current market cap of {ticker} is $ {market_cap}.\n' \
               f'1 {ticker} is valued at $ {fiat_price}.'
    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def rain( update, coin_properties ):
    ticker = coin_properties[ 'TICKER' ]
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 2:
            raise BotUserError( messages.rain_error( ticker.lower() ) )

        amount_to_rain = arguments[ 1 ]
        total_balance, wallet_balance = commonhelper.get_user_balance( user, coin_properties )
        amount_to_rain = commonhelper.get_validated_amount( amount_to_rain, user, total_balance )
        eligible_users = ActivityTracker().get_current_active_users( update, user )

        commonhelper.move_to_main( coin_properties, user, wallet_balance )

        if len( eligible_users ) == 0:
            raise BotUserError( 'Found no active users except You... :\'(' )

        eligible_users.append( Configuration.TELEGRAM_BOT_NAME )  # Give some to the bot
        amount_per_user = amount_to_rain / len( eligible_users )
        amount_per_user = round_down( amount_per_user, 8 )
        amount_remainder = round_down( amount_to_rain - amount_per_user * len( eligible_users ) + amount_per_user, 8 )
        at_users = '|'
        users_balance_changes = [ ]
        connection = database.create_connection()

        with connection:
            users_balance_changes.append( (user, ticker, str( -amount_to_rain )) )

            for eligible_user in eligible_users:
                if eligible_user is Configuration.TELEGRAM_BOT_NAME:
                    users_balance_changes.append( (eligible_user, ticker, str( amount_remainder )) )
                else:
                    users_balance_changes.append( (eligible_user, ticker, str( amount_per_user )) )
                at_users = at_users.__add__( ' @' + eligible_user + ' |' )

            database.execute_many( connection, statements.UPDATE_USER_BALANCE, users_balance_changes )

        logger.info( f'rain amount ´{amount_to_rain}´ split between {len( eligible_users )} users.' )

        return f'@{user} has rained {amount_to_rain} {ticker} to ' \
               f'{len( eligible_users )} active users: {at_users}\n{amount_per_user} ' \
               f'{ticker} received per user.'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR
