import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

# noinspection PyUnresolvedReferences
import logic.helpers.loggersetup  # needed for logging, do not remove
from db import database
from db.statements import Statements
from logic import commands
from logic.activitytracker import ActivityTracker
from logic.command import Command
from logic.common.configuration import Configuration
from logic.model.botconfiguration import BotConfiguration

logger = logging.getLogger( __name__ )


def main():
    bot_configuration = BotConfiguration( Configuration )
    connection = database.create_connection()

    with connection:
        database.init_database( connection )
        database.execute_query( connection, Statements[ 'INSERT_USER' ], (bot_configuration.telegram_bot_name,) )
        for coin in bot_configuration.coins:
            database.execute_query( connection, Statements[ 'INSERT_COIN' ], (coin.name, coin.ticker,) )

    activity_tracker = ActivityTracker()
    updater = Updater( token = bot_configuration.telegram_bot_token, request_kwargs = None )
    dispatcher = updater.dispatcher

    for coin in bot_configuration.coins:
        dispatcher.add_handler( MessageHandler( ~ Filters.command, activity_tracker.track_activity ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}commands'.lower(), Command( commands.commands, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}start'.lower(), Command( commands.help, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}help'.lower(), Command( commands.help, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}balance'.lower(), Command( commands.balance, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}deposit'.lower(), Command( commands.deposit, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}withdraw'.lower(), Command( commands.withdraw, coin ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}market'.lower(), Command( commands.market, coin, activity_tracker ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}tip'.lower(), Command( commands.tip, coin, activity_tracker ) ) )
        dispatcher.add_handler( CommandHandler( f'{coin.ticker}rain'.lower(), Command( commands.rain, coin, activity_tracker ) ) )

    updater.start_polling()

    logger.info( 'Bot started.' )


main()
