import decimal
import logging

from db import database, statements
from logic.activitytracker import ActivityTracker
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.helpers import commonhelper, markethelper
from logic.helpers.configuration import Configuration
from logic.helpers.decimalhelper import round_down

logger = logging.getLogger( __name__ )


def commands( update ):
    return messages.COMMANDS


def help( update ):
    return messages.HELP


def deposit( update ):
    try:
        user = commonhelper.get_username( update )
        deposit_address = clientcommandprocessor.run_client_command( 'getaccountaddress', None, user )
        return f'@{user}, Your depositing address is: {deposit_address}'
    except BotUserError as e:
        logger.info( e )
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def tip( update ):
    arguments = update.message.text.split( ' ' )
    try:
        if len( arguments ) < 3:
            raise BotUserError( messages.TIP_ERROR )

        user = commonhelper.get_username( update )
        target_user = arguments[ 1 ]
        amount = arguments[ 2 ]

        if '@' not in target_user:
            raise BotUserError( f'That user ´{target_user}´ is not applicable.' )

        target_user = target_user[ 1: ]
        amount = commonhelper.get_validated_amount( amount, user )

        if target_user == user:
            raise BotUserError( 'You can not tip Yourself.' )

        users_balance_changes = [ ]
        users_balance_changes.append( (user, Configuration.COIN_TICKER, str( -amount )) )
        users_balance_changes.append( (target_user, Configuration.COIN_TICKER, str( amount )) )

        connection = database.create_connection()

        with connection:
            database.execute_query( connection, statements.INSERT_USER, (target_user,) )
            database.execute_many( connection, statements.UPDATE_USER_BALANCE, users_balance_changes )

            return f'@{user} tipped @{target_user} of {amount} {Configuration.COIN_TICKER}'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def balance( update ):
    try:
        user = commonhelper.get_username( update )
        fiat_price = markethelper.get_fiat_price()
        user_balance = commonhelper.get_user_balance( user )
        user_balance = round_down( user_balance, 8 )
        fiat_balance = user_balance * decimal.Decimal( fiat_price )
        fiat_balance = round_down( fiat_balance, 2 )

        if user_balance == 0:
            message = f'@{user}, Your current balance is empty.'
        else:
            message = f'@{user}, Your current balance is: {user_balance} {Configuration.COIN_TICKER}'

        if fiat_balance != 0:
            message += f' ≈  $ {fiat_balance:.2f}'

        return message

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def withdraw( update ):
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 3:
            raise BotUserError( messages.WITHDRAW_ERROR )

        address = arguments[ 1 ]
        address = commonhelper.get_validated_address( address )
        amount = arguments[ 2 ]
        amount = commonhelper.get_validated_amount( amount, user )

        commonhelper.move_to_main( user )

        clientcommandprocessor.run_client_command( 'sendtoaddress', None, address, amount )

        try:
            connection = database.create_connection()
            with connection:
                database.execute_query( connection, statements.UPDATE_USER_BALANCE, (user, Configuration.COIN_TICKER, str( -amount ),) )
        except Exception as e:
            logger.error( e )
            return messages.GENERIC_ERROR

        return f'@{user} has successfully withdrawn to address: {address} of {amount} {Configuration.COIN_TICKER}.'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def market( update ):
    try:
        fiat_price = markethelper.get_fiat_price()
        market_cap = markethelper.get_market_cap()
        fiat_price = round( fiat_price, 4 )
        market_cap = round( market_cap, 2 )

        return f'The current market cap of {Configuration.COIN_TICKER} is $ {market_cap}.\n' \
               f'1 {Configuration.COIN_TICKER} is valued at $ {fiat_price}.'
    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR


def rain( update ):
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 1:
            raise BotUserError( messages.RAIN_ERROR )

        amount_total = arguments[ 1 ]
        amount_total = commonhelper.get_validated_amount( amount_total, user )

        eligible_users = ActivityTracker().get_current_active_users( update, user )

        if len( eligible_users ) == 0:
            raise BotUserError( 'Found no active users except You... :\'(' )

        eligible_users.append( Configuration.TELEGRAM_BOT_NAME )  # Give some to the bot
        amount_per_user = amount_total / len( eligible_users )
        amount_per_user = round_down( amount_per_user, 8 )
        amount_remainder = round_down( amount_total - amount_per_user * len( eligible_users ) + amount_per_user, 8 )
        at_users = '|'
        users_balance_changes = [ ]
        connection = database.create_connection()

        with connection:
            users_balance_changes.append( (user, Configuration.COIN_TICKER, str( -amount_total )) )

            for eligible_user in eligible_users:
                if eligible_user is Configuration.TELEGRAM_BOT_NAME:
                    users_balance_changes.append( (eligible_user, Configuration.COIN_TICKER, str( amount_remainder )) )
                else:
                    users_balance_changes.append( (eligible_user, Configuration.COIN_TICKER, str( amount_per_user )) )
                at_users = at_users.__add__( ' @' + eligible_user + ' |' )

            database.execute_many( connection, statements.UPDATE_USER_BALANCE, users_balance_changes )

        logger.info( f'rain amount ´{amount_total}´ split between {len( eligible_users )} users.' )

        return f'@{user} has rained {amount_total} {Configuration.COIN_TICKER} to ' \
               f'{len( eligible_users )} active users: {at_users}\n{amount_per_user} ' \
               f'{Configuration.COIN_TICKER} received per user.'

    except BotUserError as e:
        return e.message
    except Exception as e:
        logger.error( e )
        logger.exception( "message" )
        return messages.GENERIC_ERROR
