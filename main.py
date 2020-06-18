import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# noinspection PyUnresolvedReferences
import logic.helpers.loggersetup  # needed for logging, do not remove
from db import database, statements
from logic import commands
from logic.activitytracker import ActivityTracker
from logic.command import Command
from logic.common.configuration import Configuration

logger = logging.getLogger( __name__ )


def main():
    connection = database.create_connection()

    with connection:
        database.init_database( connection )
        database.execute_query( connection, statements.INSERT_USER, (Configuration.TELEGRAM_BOT_NAME,) )
        for coin in Configuration.COINS:
            database.execute_query( connection, statements.INSERT_COIN, (coin[ 'NAME' ], coin[ 'TICKER' ],) )

    activity_tracker = ActivityTracker()
    updater = Updater( token = Configuration.TELEGRAM_BOT_TOKEN, request_kwargs = None )
    dispatcher = updater.dispatcher

    for coin in Configuration.COINS:
        dispatcher.add_handler( MessageHandler( ~ Filters.command, activity_tracker.track_activity ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}commands'.lower(), Command( commands.commands, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}start'.lower(), Command( commands.help, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}help'.lower(), Command( commands.help, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}balance'.lower(), Command( commands.balance, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}deposit'.lower(), Command( commands.deposit, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}withdraw'.lower(), Command( commands.withdraw, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}market'.lower(), Command( commands.market, coin, activity_tracker ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}tip'.lower(), Command( commands.tip, coin, activity_tracker ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin[ "TICKER" ]}rain'.lower(), Command( commands.rain, coin, activity_tracker ) ) )

    updater.start_polling()

    logger.info( 'Bot started.' )


main()
