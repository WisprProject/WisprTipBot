import decimal
import logging

from db import database
from db.statements import Statements
from logic.activitytracker import ActivityTracker
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.common.configuration import Configuration
from logic.helpers import commonhelper, markethelper
from logic.helpers.decimalhelper import round_down
from logic.model.blockchainexplorerconfiguration import BlockchainExplorerConfiguration
from logic.model.coinproperties import CoinProperties

logger = logging.getLogger( __name__ )


def commands( update, coin_properties: CoinProperties ):
    return messages.commands( coin_properties.ticker.lower() ),


def help( update, coin_properties: CoinProperties ):
    return messages.help( coin_properties.ticker.lower() ),


def market( update, coin_properties: CoinProperties ):
    ticker = coin_properties.ticker
    fiat_price = markethelper.get_fiat_price( ticker )
    market_cap = markethelper.get_market_cap( ticker )
    fiat_price = round_down( fiat_price, 2 )
    market_cap = round( market_cap, 2 )

    return f'The current market cap of {ticker} is $ {market_cap}.\n' \
           f'1 {ticker} is valued at $ {fiat_price}.',


def balance( update, coin_properties: CoinProperties ):
    ticker = coin_properties.ticker
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

    return message,


def deposit( update, coin_properties: CoinProperties ):
    user = commonhelper.get_username( update )
    deposit_address = clientcommandprocessor.run_client_command( coin_properties.rpc_configuration, 'getaccountaddress', None, user )

    return f'@{user}, Your depositing address is: {deposit_address}',


def withdraw( update, coin_properties: CoinProperties ):
    ticker = coin_properties.ticker
    arguments = update.message.text.split( ' ' )

    user = commonhelper.get_username( update )

    if len( arguments ) < 3:
        raise BotUserError( messages.withdraw_error( ticker.lower() ) )

    address = arguments[ 1 ]
    address = commonhelper.get_validated_address( address, coin_properties )
    amount = arguments[ 2 ]
    total_balance, wallet_balance = commonhelper.get_user_balance( user, coin_properties )
    amount = commonhelper.get_validated_amount( amount, user, total_balance )
    configured_transaction_fee = round_down( coin_properties.withdrawal_fee, 8 )

    if amount < coin_properties.minimum_withdraw:
        raise BotUserError( f'Minimum allowed withdrawal amount is {configured_transaction_fee}{ticker}.' )

    if arguments[ 2 ].lower is 'all':
        amount -= configured_transaction_fee
    elif amount + configured_transaction_fee > total_balance:
        raise BotUserError( f'Unable to withdraw {amount}{ticker}. '
                            f'Amount combined with withdrawal fee {configured_transaction_fee}{ticker} exceeds the available balance: '
                            f'{round_down( amount + configured_transaction_fee, 8 )}{ticker} > {round_down( total_balance, 8 )}{ticker}.' )

    commonhelper.move_to_main( coin_properties, user, wallet_balance )
    transaction_id = clientcommandprocessor.run_client_command( coin_properties.rpc_configuration, 'sendtoaddress', None, address, amount )
    real_transaction_fee = commonhelper.get_transaction_fee( coin_properties.rpc_configuration, transaction_id )

    users_balance_changes = [ (user, ticker, str( -amount - configured_transaction_fee )),
                              (Configuration.TELEGRAM_BOT_NAME, ticker, str( configured_transaction_fee + real_transaction_fee )) ]

    try:
        connection = database.create_connection()
        with connection:
            database.execute_many( connection, Statements[ 'UPDATE_USER_BALANCE' ], users_balance_changes )
    except Exception as e:
        logger.error( e )
        return messages.GENERIC_ERROR

    blockchain_explorer: BlockchainExplorerConfiguration = coin_properties.blockchain_explorer

    if blockchain_explorer is not None:
        address = f'<a href="{blockchain_explorer.url}/{blockchain_explorer.address_prefix}/{address}">{address}</a>'
        transaction_id = f'<a href="{blockchain_explorer.url}/{blockchain_explorer.tx_prefix}/{transaction_id}">{transaction_id}</a>'

    return f'@{user} has successfully withdrawn {amount}{ticker} to address: {address}.<pre>\r\n</pre>TX:&#160;{transaction_id}. ' \
           f'Withdrawal fee of {configured_transaction_fee}{ticker} was applied.', 'HTML'


def tip( update, coin_properties: CoinProperties ):
    ticker = coin_properties.ticker
    arguments = update.message.text.split( ' ' )

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
        database.execute_query( connection, Statements[ 'INSERT_USER' ], (target_user,) )
        database.execute_many( connection, Statements[ 'UPDATE_USER_BALANCE' ], users_balance_changes )

    return f'@{user} tipped @{target_user} of {amount} {ticker}',


def rain( update, coin_properties: CoinProperties ):
    ticker = coin_properties.ticker
    arguments = update.message.text.split( ' ' )
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

        database.execute_many( connection, Statements[ 'UPDATE_USER_BALANCE' ], users_balance_changes )

    logger.info( f'rain amount ´{amount_to_rain}´ split between {len( eligible_users )} users.' )

    return f'@{user} has rained {amount_to_rain} {ticker} to ' \
           f'{len( eligible_users )} active users: {at_users}\n{amount_per_user} ' \
           f'{ticker} received per user.',
