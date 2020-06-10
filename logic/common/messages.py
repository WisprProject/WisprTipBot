HELP = 'The following commands are at your disposal: /help, /commands, /deposit, /balance, /tip, /withdraw, ' \
       '/market and /rain.\n\n' \
       'Tipping format:\n' \
       '/tip <user> <amount>\n\n' \
       'Withdrawing format:\n' \
       '/withdraw <address> <amount>\n\n' \
       'Rain format:\n' \
       '/rain <amount>'

COMMANDS = 'Initiating commands /tip, /withdraw and /rain have a specific format,\n' \
           'use them like so:\n\n' \
           'Parameters:\n' \
           '<user> = target user to tip\n' \
           '<amount> = amount of coins to utilise\n' \
           '<address> = address to withdraw to\n\n' \
           'Tipping format:\n' \
           '/tip <user> <amount>\n\n' \
           'Withdrawing format:\n' \
           '/withdraw <address> <amount>\n\n' \
           'Rain format:\n' \
           '/rain <amount>'

TIP_ERROR = 'You have to specify the tip recipient and the amount You want to tip.\n' \
            '/tip @<user> <amount>'

WITHDRAW_ERROR = 'You have to specify the withdrawal address and the amount You want to withdraw.\n' \
                 '/withdraw <address> <amount>'

RAIN_ERROR = 'You have to specify the amount that You want to rain.\n' \
             '/rain <amount>'

SET_USERNAME = '<UnknownUser>, please set the telegram username in Your profile settings!'

GENERIC_ERROR = 'An error occurred during handling the command. Contact the bot support.'
