def help( ticker ):
    return f'The following commands are at your disposal: /{ticker}help, /{ticker}commands, /{ticker}deposit, /{ticker}balance, /{ticker}tip, ' \
           f'/{ticker}withdraw, ' \
           f'/{ticker}market and /{ticker}rain.\n\n' \
           'Tipping format:\n' \
           f'/{ticker}tip <user> <amount>\n\n' \
           f'Withdrawing format:\n' \
           f'/{ticker}withdraw <address> <amount>\n\n' \
           'Rain format:\n' \
           f'/{ticker}rain <amount>'


def commands( ticker ):
    return f'Initiating commands /{ticker}tip, /{ticker}withdraw and /{ticker}rain have a specific format,\n' \
           'use them like so:\n\n' \
           'Parameters:\n' \
           '<user> = target user to tip\n' \
           '<amount> = amount of coins to utilise\n' \
           '<address> = address to withdraw to\n\n' \
           'Tipping format:\n' \
           f'/{ticker}tip <user> <amount>\n\n' \
           'Withdrawing format:\n' \
           f'/{ticker}withdraw <address> <amount>\n\n' \
           'Rain format:\n' \
           f'/{ticker}rain <amount>'


def tip_error( ticker ):
    return 'You have to specify the tip recipient and the amount You want to tip.\n' \
           f'/{ticker}tip @<user> <amount>'


def withdraw_error( ticker ):
    return 'You have to specify the withdrawal address and the amount You want to withdraw.\n' \
           f'/{ticker}withdraw <address> <amount>'


def rain_error( ticker ):
    return 'You have to specify the amount that You want to rain.\n' \
           f'/{ticker}rain <amount>'


SET_USERNAME = '<UnknownUser>, please set the telegram username in Your profile settings!'

GENERIC_ERROR = 'An error occurred during handling the command. Contact the bot support.'
