import logging

from logic.activitytracker import ActivityTracker
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.helpers import commonhelper, markethelper
from logic.helpers.configuration import Configuration


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
        logging.info( e )
        return e.message


def tip( update ):
    arguments = update.message.text.split( ' ' )
    try:
        if len( arguments ) < 3:
            raise BotUserError( messages.TIP_ERROR )

        user = commonhelper.get_username( update )
        target = arguments[ 1 ]
        amount = arguments[ 2 ]

        if '@' not in target:
            raise BotUserError( f'That user ´{target}´ is not applicable.' )

        target = target[ 1: ]
        amount = commonhelper.get_validated_amount( amount, user )

        if target == user:
            raise BotUserError( 'You can not tip Yourself.' )

        if clientcommandprocessor.run_client_command( 'move', None, user, target, amount ):
            return f'@{user} tipped @{target} of {amount} {Configuration.COIN_SYMBOL}'
        else:
            raise BotUserError( messages.GENERIC_ERROR )

    except BotUserError as e:
        return e.message
    except ValueError:
        return messages.GENERIC_ERROR


def balance( update ):
    try:
        user = commonhelper.get_username( update )
        fiat_price = 0

        try:
            fiat_price = markethelper.get_fiat_price()
        except BotUserError as e:
            logging.warning( e.message )

        user_balance = commonhelper.get_user_balance( user )
        fiat_balance = user_balance * fiat_price
        fiat_balance = round( fiat_balance, 3 )
        user_balance_rounded = round( user_balance, 3 )

        if user_balance_rounded == 0:
            if user_balance != 0:
                message = f'@{user}, Your current balance is almost empty, still some dust can be found.'
            else:
                message = f'@{user}, Your current balance is empty.'
        elif fiat_balance == 0:
            message = f'@{user}, Your current balance is: {user_balance_rounded} {Configuration.COIN_SYMBOL}'
        else:
            message = f'@{user}, Your current balance is: {user_balance_rounded} {Configuration.COIN_SYMBOL} ' \
                      f'≈  $ {fiat_balance}'

        return message

    except BotUserError as e:
        return e.message


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

        clientcommandprocessor.run_client_command( 'sendfrom', None, user, address, amount )
        return f'@{user} has successfully withdrawn to address: {address} of {amount} {Configuration.COIN_SYMBOL}.'

    except BotUserError as e:
        return e.message
    except ValueError:
        return messages.GENERIC_ERROR


def market( update ):
    try:
        fiat_price = markethelper.get_fiat_price()
        market_cap = markethelper.get_market_cap()
        fiat_price = round( fiat_price, 4 )
        market_cap = round( market_cap, 2 )

        return f'The current market cap of {Configuration.COIN_SYMBOL} is $ {market_cap}.\n' \
               f'1 {Configuration.COIN_SYMBOL} is valued at $ {fiat_price}.'
    except BotUserError as e:
        return e.message


def rain( update ):
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 2:
            raise BotUserError( messages.RAIN_ERROR )

        amount_total = arguments[ 1 ]
        amount_total = commonhelper.get_validated_amount( amount_total, user )

        eligible_users = ActivityTracker().get_current_active_users( update, user )

        if len( eligible_users ) <= 0:
            raise BotUserError( 'Found no active users except You... :\'(' )

        eligible_users.append( Configuration.TELEGRAM_BOT_NAME )  # Give some to the bot
        amount_per_user = float( amount_total ) / len( eligible_users )
        amount_per_user = round( amount_per_user, 8 )
        at_users = '|'

        for eligible_user in eligible_users:
            clientcommandprocessor.run_client_command( 'move', None, user, eligible_user, amount_per_user )
            logging.info( f'rain amount ´{amount_per_user}´ sent to {eligible_user}' )
            at_users = at_users.__add__( ' @' + eligible_user + ' |' )

        return f'@{user} has rained {amount_total} {Configuration.COIN_SYMBOL} to ' \
               f'{len( eligible_users )} active users: {at_users}\n{amount_per_user} ' \
               f'{Configuration.COIN_SYMBOL} received per user.'

    except BotUserError as e:
        return e.message
    except ValueError:
        return messages.GENERIC_ERROR
