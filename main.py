import logic.helpers.loggersetup
import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from db import database
from logic import commands
from logic.activitytracker import ActivityTracker
from logic.command import Command
from logic.helpers.configuration import Configuration

logger = logging.getLogger( __name__ )


def main():
    connection = database.create_connection()

    with connection:
        database.init_database( connection )

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
