import logging
from logic import commandprocessor, messages

from logic.activitytracker import ActivityTracker
from logic.botusererror import BotUserError
from logic.helpers.configuration import Configuration
from logic.helpers import commonhelper, markethelper


def commands( bot, update ):
    bot.send_message( chat_id = update.message.chat_id, text = messages.COMMANDS )


def help( bot, update ):
    bot.send_message( chat_id = update.message.chat_id, text = messages.HELP )


def deposit( bot, update ):
    try:
        user = commonhelper.get_username( update )
        deposit_address = commandprocessor.run_wallet_command( [ 'getaccountaddress', user ] )
        bot.send_message( chat_id = update.message.chat_id,
                          text = f'@{user}, Your depositing address is: {deposit_address}' )
    except BotUserError as e:
        bot.send_message( chat_id = update.message.chat_id, text = e.message )
        logging.info( e )


def tip( bot, update ):
    chat_id = update.message.chat_id
    arguments = update.message.text.split( ' ' )
    try:
        if len( arguments ) < 3:
            raise BotUserError( messages.TIP_ERROR )

        user = commonhelper.get_username( update )
        target = arguments[ 1 ]
        amount = arguments[ 2 ]
        machine = '@' + Configuration.TELEGRAM_BOT_NAME

        if '@' not in target:
            raise BotUserError( f'That user ´{target}´ is not applicable.' )

        target = target[ 1: ]
        amount = commonhelper.get_validated_amount( amount, user )

        if target == user:
            raise BotUserError( 'You can not tip Yourself.' )

        if commandprocessor.run_wallet_command( [ 'move', user, target, amount ] ):
            bot.send_message( chat_id = chat_id,
                              text = f'@{user} tipped @{target} of {amount} {Configuration.COIN_SYMBOL}' )
        else:
            raise BotUserError( messages.GENERIC_ERROR )

    except BotUserError as e:
        bot.send_message( chat_id = chat_id, text = e.message )
    except ValueError:
        bot.send_message( chat_id = chat_id,
                          text = messages.GENERIC_ERROR )


def balance( bot, update ):
    try:
        user = commonhelper.get_username( update )
        fiat_price = markethelper.get_fiat_price()
        user_balance = commonhelper.get_user_balance( user )
        fiat_balance = user_balance * fiat_price
        fiat_balance = round( fiat_balance, 3 )
        user_balance_rounded = round( user_balance, 3 )

        if user_balance_rounded == 0:
            if user_balance != 0:
                message = f'@{user}, Your current balance is almost empty, still some dust can be found.'
            else:
                message = f'@{user}, Your current balance is empty.'
        else:
            message = f'@{user}, Your current balance is: {user_balance_rounded} {Configuration.COIN_SYMBOL} ' \
                f'≈  $ {fiat_balance}'

        bot.send_message( chat_id = update.message.chat_id, text = message )

    except BotUserError as e:
        bot.send_message( chat_id = update.message.chat_id, text = e.message )


def withdraw( bot, update ):
    chat_id = update.message.chat_id
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 3:
            raise BotUserError( messages.WITHDRAW_ERROR )

        address = arguments[ 1 ]
        address = commonhelper.get_validated_address( address )
        amount = arguments[ 2 ]
        amount = commonhelper.get_validated_amount( amount, user )

        commandprocessor.run_wallet_command( [ 'sendfrom', user, address, amount ] )
        bot.send_message( chat_id = chat_id,
                          text = f'@{user} has successfully withdrawn to address: {address} of {amount} '
                          f'{Configuration.COIN_SYMBOL}.' )

    except BotUserError as e:
        bot.send_message( chat_id = chat_id, text = e.message )
    except ValueError:
        bot.send_message( chat_id = chat_id,
                          text = messages.GENERIC_ERROR )


def market( bot, update ):
    fiat_price = markethelper.get_fiat_price()
    market_cap = markethelper.get_market_cap()
    fiat_price = round( fiat_price, 4 )
    market_cap = round( market_cap, 2 )
    bot.send_message( chat_id = update.message.chat_id,
                      text = f'The current market cap of {Configuration.COIN_SYMBOL} is $ {market_cap}.\n'
                      f'1 {Configuration.COIN_SYMBOL} is valued at $ {fiat_price}.' )


def rain( bot, update ):
    chat_id = update.message.chat_id
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
        amount_per_user = str( amount_per_user )
        at_users = '|'

        for eligible_user in eligible_users:
            commandprocessor.run_wallet_command( [ 'move', user, eligible_user, amount_per_user ] )
            logging.info( f'rain amount ´{amount_per_user}´ sent to {eligible_user}' )
            at_users = at_users.__add__( ' @' + eligible_user + ' |' )

        bot.send_message( chat_id = chat_id,
                          text = f'@{user} has rained {amount_total} {Configuration.COIN_SYMBOL} to '
                          f'{len( eligible_users )} active users: {at_users}\n{amount_per_user} '
                          f'{Configuration.COIN_SYMBOL} received per user.' )

    except BotUserError as e:
        bot.send_message( chat_id = chat_id, text = e.message )
    except ValueError:
        bot.send_message( chat_id = chat_id, text = messages.GENERIC_ERROR )
