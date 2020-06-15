import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# noinspection PyUnresolvedReferences
import logic.helpers.loggersetup  # needed for logging, do not remove
from db import database, statements
from logic import commands
from logic.activitytracker import ActivityTracker
from logic.command import Command
from logic.helpers.configuration import Configuration

logger = logging.getLogger( __name__ )


def main():
    connection = database.create_connection()

    with connection:
        database.init_database( connection )
        database.execute_query( connection, statements.INSERT_USER, (Configuration.TELEGRAM_BOT_NAME,) )
        database.execute_query( connection, statements.INSERT_COIN, (Configuration.COIN_NAME, Configuration.COIN_TICKER,) )

    activity_tracker = ActivityTracker()
    updater = Updater( token = Configuration.TELEGRAM_BOT_TOKEN, request_kwargs = None )
    dispatcher = updater.dispatcher

    dispatcher.add_handler( MessageHandler( ~ Filters.command, activity_tracker.track_activity ) )
    dispatcher.add_handler( CommandHandler( 'commands', Command( commands.commands ) ) )
    dispatcher.add_handler( CommandHandler( 'start', Command( commands.help ) ) )
    dispatcher.add_handler( CommandHandler( 'help', Command( commands.help ) ) )
    dispatcher.add_handler( CommandHandler( 'balance', Command( commands.balance ) ) )
    dispatcher.add_handler( CommandHandler( 'deposit', Command( commands.deposit ) ) )
    dispatcher.add_handler( CommandHandler( 'withdraw', Command( commands.withdraw ) ) )
    dispatcher.add_handler( CommandHandler( 'market', Command( commands.market, activity_tracker ) ) )
    dispatcher.add_handler( CommandHandler( 'tip', Command( commands.tip, activity_tracker ) ) )
    dispatcher.add_handler( CommandHandler( 'rain', Command( commands.rain, activity_tracker ) ) )

    updater.start_polling()

    logger.info( 'Bot started.' )


main()
