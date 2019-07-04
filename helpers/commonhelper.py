import commandprocessor

from messagetouser import Message
from botusererror import BotUserError


def get_username( update ):
    user = update.message.from_user.username
    if user is not None:
        return user
    raise BotUserError( Message.SET_USERNAME )


def get_validated_address( address ):
    if len( address ) == 34:
        command = [ 'validateaddress', address ]
        if commandprocessor.run_wallet_command( command, 'isvalid' ):
            return address

    raise BotUserError( '´{0}´ is not a valid address.'.format( address ) )


def get_user_balance( user ):
    try:
        command = [ 'getbalance', user ]
        user_balance = commandprocessor.run_wallet_command( command )
        return float( user_balance )
    except BotUserError:
        raise BotUserError


def get_validated_amount( amount, user ):
    try:
        if amount.lower() == 'all':
            amount = get_user_balance(user)
        else:
            amount = float( amount )
    except ValueError:
        raise BotUserError( '´{0}´ is not a valid amount'.format( amount ) )

    if amount <= 0:
        raise BotUserError( 'Amount ´{0}´ has to be bigger than 0'.format( amount ) )

    user_balance = get_user_balance( user )

    if user_balance < amount:
        raise BotUserError( '@{0} You have insufficient funds.'.format( user ) )

    return str( amount )
