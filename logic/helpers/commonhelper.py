import decimal

from db import database, statements
from logic.common import clientcommandprocessor, messages
from logic.common.botusererror import BotUserError
from logic.helpers.decimalhelper import round_down


def get_username( update ):
    user = update.message.from_user.username

    if user is not None:
        return user

    raise BotUserError( messages.SET_USERNAME )


def get_validated_address( address ):
    if len( address ) == 34:
        if clientcommandprocessor.run_client_command( 'validateaddress', 'isvalid', address ):
            return address

    raise BotUserError( f'´{address}´ is not a valid address.' )


def get_user_balance( user ):
    try:
        user_balance = clientcommandprocessor.run_client_command( 'getbalance', None, user )
        connection = database.create_connection()

        with connection:
            user_off_chain_balance = database.fetch_result( connection, statements.SELECT_USER_OFF_CHAIN_BALANCE, (user,) )

        if user_off_chain_balance is None:
            user_off_chain_balance = 0

        user_off_chain_balance = round_down( user_off_chain_balance )
        
        return user_balance + decimal.Decimal( user_off_chain_balance )
    except BotUserError:
        raise BotUserError


def get_validated_amount( amount, user ):
    try:
        if amount.lower() == 'all':
            amount = get_user_balance( user )
        else:
            amount = decimal.Decimal( amount )
    except ValueError:
        raise BotUserError( f'´{amount}´ is not a valid amount' )

    if amount <= 0:
        raise BotUserError( f'Amount has to be bigger than 0' )

    if float( amount ) < 0.1:
        raise BotUserError( f'Amount has to be greater or equal to 0.1' )

    user_balance = get_user_balance( user )

    if user_balance < amount:
        raise BotUserError( f'@{user}, You have insufficient funds.' )

    return round_down( amount, 8 )
