from db import database
from db.statements import Statements
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.helpers.decimalhelper import round_down
from logic.model.coinproperties import CoinProperties
from logic.model.rpcconfiguration import RpcConfiguration


def get_username( update ):
    user = update.message.from_user.username

    if user is not None:
        return user

    raise BotUserError( messages.SET_USERNAME )


def get_validated_address( address, coin_properties: CoinProperties ):
    if len( address ) == 34:
        if clientcommandprocessor.run_client_command( coin_properties.rpc_configuration, 'validateaddress', 'isvalid', address ):
            return address

    raise BotUserError( f'´{address}´ is not a valid address.' )


def get_user_balance( user, coin_properties: CoinProperties ):
    try:
        user_balance = clientcommandprocessor.run_client_command( coin_properties.rpc_configuration, 'getbalance', None, user )
        connection = database.create_connection()

        with connection:
            user_off_chain_balance = database.fetch_result( connection, Statements[ 'SELECT_USER_OFF_CHAIN_BALANCE' ], (user, coin_properties.ticker) )

        if user_off_chain_balance is None:
            user_off_chain_balance = 0

        user_off_chain_balance = round_down( user_off_chain_balance, 8 )
        total_balance = user_balance + user_off_chain_balance

        return total_balance, user_balance
    except BotUserError:
        raise BotUserError


def get_validated_amount( amount, user, user_balance ):
    try:
        if amount.lower() == 'all':
            amount = user_balance
        else:
            amount = round_down( amount, 8 )
    except ValueError:
        raise BotUserError( f'´{amount}´ is not a valid amount' )

    if amount <= 0:
        raise BotUserError( f'Amount has to be bigger than 0' )

    if float( amount ) < 0.1:
        raise BotUserError( f'Amount has to be greater or equal to 0.1' )

    if user_balance < amount:
        raise BotUserError( f'@{user}, You have insufficient funds.' )

    return amount


def move_to_main( coin_properties: CoinProperties, user, wallet_balance ):
    if wallet_balance <= 0:
        return

    if clientcommandprocessor.run_client_command( coin_properties.rpc_configuration, 'move', None, user, '', wallet_balance ):
        connection = database.create_connection()
        with connection:
            database.execute_query( connection, Statements[ 'INSERT_USER' ], (user,) )
            database.execute_query( connection, Statements[ 'UPDATE_USER_BALANCE' ], (user, coin_properties.ticker, str( wallet_balance ),) )
    else:
        raise Exception( f'Failed to move {user} balance {wallet_balance} to main account.' )


def get_transaction_fee( rpc_configuration: RpcConfiguration, transaction_id ):
    if transaction_id is None:
        raise Exception( 'Transaction id is missing' )

    return clientcommandprocessor.run_client_command( rpc_configuration, 'gettransaction', 'fee', transaction_id )
