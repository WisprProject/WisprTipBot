import commandprocessor
import logging

from botusererror import BotUserError
from configuration import Configuration
from datetime import datetime
from helpers import markethelper
from helpers import commonhelper
from messagetouser import Message
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def init():
    global active_users
    active_users = None


init()


def commands( bot, update ):
    activity_tracker(bot, update)
    bot.send_message( chat_id=update.message.chat_id, text=Message.COMMANDS )


def help( bot, update ):
    activity_tracker(bot, update)
    # keyboard = [ [ InlineKeyboardButton( "Option 1", callback_data='1' ),
    #                InlineKeyboardButton( "Option 2", callback_data='2' ) ],
    #
    #              [ InlineKeyboardButton( "Option 3", callback_data='3' ) ] ]
    #
    # reply_markup = InlineKeyboardMarkup( keyboard )
    #
    # update.message.reply_text( 'Please choose:', reply_markup=reply_markup )
    bot.send_message( chat_id=update.message.chat_id, text=Message.HELP )


#
# def button( bot, update ):
#     query = update.callback_query
#     query.edit_message_text( text="Selected option: {}".format( query.data ) )


def deposit( bot, update ):
    activity_tracker(bot, update)
    try:
        user = commonhelper.get_username( update )
        deposit_address = commandprocessor.run_wallet_command( [ 'getaccountaddress', user ] )
        bot.send_message( chat_id=update.message.chat_id,
                          text='@{0}, Your depositing address is: {1}'.format( user, deposit_address ) )
    except BotUserError as e:
        bot.send_message( chat_id=update.message.chat_id, text=e.message )
        logger.debug( e )


def tip( bot, update ):
    activity_tracker(bot, update)
    chat_id = update.message.chat_id
    arguments = update.message.text.split( ' ' )
    try:
        if len( arguments ) < 3:
            raise BotUserError( Message.TIP_ERROR )

        user = commonhelper.get_username( update )
        target = arguments[ 1 ]
        amount = arguments[ 2 ]
        machine = '@' + Configuration.TELEGRAM_BOT_NAME

        # TODO: Question of business logic
        if target == machine:
            raise BotUserError( 'Can not tip the bot.' )

        if '@' not in target:
            raise BotUserError( 'That user ´{0}´ is not applicable.'.format( target ) )

        target = target[ 1: ]
        amount = commonhelper.get_validated_amount( amount, user )

        if target == user:
            raise BotUserError( 'You can not tip Yourself.' )

        if commandprocessor.run_wallet_command( [ 'move', user, target, amount ] ):
            bot.send_message( chat_id=chat_id,
                              text='@{0} tipped @{1} of {2} {3}'.format( user, target, amount,
                                                                         Configuration.COIN_SYMBOL ) )
        else:
            raise BotUserError( Message.GENERIC_ERROR )

    except BotUserError as e:
        bot.send_message( chat_id=chat_id, text=e.message )
    except ValueError:
        bot.send_message( chat_id=chat_id,
                          text=Message.GENERIC_ERROR )


def balance( bot, update ):
    activity_tracker(bot, update)
    try:
        user = commonhelper.get_username( update )
        fiat_price = markethelper.get_fiat_price()
        user_balance = commonhelper.get_user_balance( user )
        fiat_balance = user_balance * fiat_price
        fiat_balance = round( fiat_balance, 3 )
        user_balance = round( user_balance, 3 )
        if user_balance == 0:
            message = '@{0}, Your current balance is empty.'.format( user )
        else:
            message = '@{0}, Your current balance is: {1} {2} ≈  $ {3}'.format( user, user_balance,
                                                                                Configuration.COIN_SYMBOL,
                                                                                fiat_balance )
        bot.send_message( chat_id=update.message.chat_id,
                          text=message )
    except BotUserError as e:
        bot.send_message( chat_id=update.message.chat_id,
                          text=e.message )


def withdraw( bot, update ):
    activity_tracker(bot, update)
    chat_id = update.message.chat_id
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 3:
            raise BotUserError( Message.WITHDRAW_ERROR )

        address = arguments[ 1 ]
        address = commonhelper.get_validated_address( address )
        amount = arguments[ 2 ]
        amount = commonhelper.get_validated_amount( amount, user )

        commandprocessor.run_wallet_command( 'sendfrom' + arguments )
        bot.send_message( chat_id=chat_id,
                          text='@{0} has successfully withdrawn to address: {1} of {2} {3}.'.format(
                                  user, address, amount, Configuration.COIN_SYMBOL ) )

    except BotUserError as e:
        bot.send_message( chat_id=chat_id, text=e.message )
    except ValueError:
        bot.send_message( chat_id=chat_id,
                          text=Message.GENERIC_ERROR )


def market( bot, update ):
    activity_tracker(bot, update)
    fiat_price = markethelper.get_fiat_price()
    market_cap = markethelper.get_market_cap()
    fiat_price = round( fiat_price, 4 )
    market_cap = round( market_cap, 2 )
    bot.send_message( chat_id=update.message.chat_id,
                      text='The current market cap of {0} is $ {1}.\n'
                           '1 {0} is valued at $ {2}.'.format( Configuration.COIN_SYMBOL, market_cap, fiat_price ) )


def rain( bot, update ):
    activity_tracker(bot, update)
    chat_id = update.message.chat_id
    arguments = update.message.text.split( ' ' )
    try:
        user = commonhelper.get_username( update )

        if len( arguments ) < 2:
            raise BotUserError( Message.RAIN_ERROR )

        amount_total = arguments[ 1 ]
        amount_total = commonhelper.get_validated_amount( amount_total, user )

        eligible_users = get_eligible_active_users( update, user )
        if len( eligible_users ) > 0:
            amount_per_user = float( amount_total ) / len( eligible_users )
            amount_per_user = str( amount_per_user )
            at_users = '|'

            for eligible_user in eligible_users:
                commandprocessor.run_wallet_command( [ 'move', user, eligible_user, amount_per_user ] )
                logger.info( 'rain amount sent to ' + eligible_user )
                at_users = at_users.__add__(' @' + eligible_user + ' |')

            message = '@{0} has rained {1} {2} to {3} active users: {4}\n' \
                      '{5} {2} received per user.' \
                .format( user, amount_total, Configuration.COIN_SYMBOL, len( eligible_users ), at_users, amount_per_user )
        else:
            message = 'Found no active users except You... :\'('
        bot.send_message( chat_id=chat_id,
                          text=message )
    except BotUserError as e:
        bot.send_message( chat_id=chat_id, text=e.message )
    except ValueError:
        bot.send_message( chat_id=chat_id, text=Message.GENERIC_ERROR )


def activity_tracker( bot, update ):
    global active_users
    chat_id = update.message.chat_id
    now = datetime.now()
    current_time = datetime.timestamp( now )
    user = commonhelper.get_username( update )
    if active_users is None:
        active_users = { chat_id: { user: current_time } }
    elif chat_id not in active_users:
        active_users.update( { chat_id: { user: current_time } } )
    else:
        if user not in active_users[ chat_id ]:
            active_users[ chat_id ].update( { user: current_time } )
        else:
            active_users[ chat_id ][ user ] = current_time
    logger.debug( '@{0} spoke @{1} at {2}.'.format( user, chat_id, active_users[ chat_id ][ user ] ) )


def get_eligible_active_users( update, user ):
    global active_users
    eligible_users = [ ]
    chat_id = update.message.chat_id
    if active_users is not None and active_users[ chat_id ] is not None:
        for active_user in active_users[ chat_id ]:
            now = datetime.now()
            current_time = datetime.timestamp( now )
            if current_time - active_users[ chat_id ][
                active_user ] <= Configuration.CHAT_ACTIVITY_TIME and active_user != user:
                eligible_users.append( active_user )
    if len( eligible_users ) is 0:
        logger.debug(
                'No eligible users for receiving rain in chatId: {0} found from active users: {1}'.format( chat_id,
                                                                                                           active_users ) )
    return eligible_users
