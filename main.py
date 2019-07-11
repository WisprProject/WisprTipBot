import logging
import os

from datetime import datetime
from logic import commands
from logic.helpers.configuration import Configuration
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

now = datetime.now().strftime( '%Y%m%d-%H%M%S' )
log_filename = f'logs/{now}.log'
os.makedirs( os.path.dirname( log_filename ), exist_ok = True )
log_formatter = logging.Formatter( '%(levelname).1s %(asctime)s %(message)s [%(name)s]' )
logging.basicConfig( format='%(levelname).1s %(asctime)s %(message)s [%(name)s]', level=Configuration.LOGGING_LEVEL )
logger = logging.getLogger( __name__ )
file_handler = logging.FileHandler( log_filename )
file_handler.setFormatter( log_formatter )
logger.addHandler( file_handler )


def main():
    updater = Updater( token=Configuration.TELEGRAM_BOT_TOKEN, request_kwargs=None )
    dispatcher = updater.dispatcher

    dispatcher.add_handler( MessageHandler( ~ Filters.command, commands.activity_tracker ) )
    dispatcher.add_handler( CommandHandler( 'commands', commands.commands ) )
    dispatcher.add_handler( CommandHandler( 'start', commands.help ) )
    dispatcher.add_handler( CommandHandler( 'help', commands.help ) )
    dispatcher.add_handler( CommandHandler( 'balance', commands.balance ) )
    dispatcher.add_handler( CommandHandler( 'deposit', commands.deposit ) )
    dispatcher.add_handler( CommandHandler( 'withdraw', commands.withdraw ) )
    dispatcher.add_handler( CommandHandler( 'market', commands.market ) )
    dispatcher.add_handler( CommandHandler( 'tip', commands.tip ) )
    dispatcher.add_handler( CommandHandler( 'rain', commands.rain ) )

    updater.start_polling()

    logger.info( 'Bot started.' )


main()
