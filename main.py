import command
import logging

from configuration import Configuration
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=Configuration.LOGGING_LEVEL )
logger = logging.getLogger( __name__ )


def main():
    updater = Updater( token=Configuration.TELEGRAM_BOT_TOKEN, request_kwargs=None )
    dispatcher = updater.dispatcher

    # dispatcher.add_handler( CallbackQueryHandler( command.button ) )
    dispatcher.add_handler( MessageHandler( ~ Filters.command, command.activity_tracker ) )
    dispatcher.add_handler( CommandHandler( 'commands', command.commands ) )
    dispatcher.add_handler( CommandHandler( 'start', command.help ) )
    dispatcher.add_handler( CommandHandler( 'help', command.help ) )
    dispatcher.add_handler( CommandHandler( 'balance', command.balance ) )
    dispatcher.add_handler( CommandHandler( 'deposit', command.deposit ) )
    dispatcher.add_handler( CommandHandler( 'withdraw', command.withdraw ) )
    dispatcher.add_handler( CommandHandler( 'market', command.market ) )
    dispatcher.add_handler( CommandHandler( 'tip', command.tip ) )
    dispatcher.add_handler( CommandHandler( 'rain', command.rain ) )

    updater.start_polling()

    logger.info( 'Bot started.' )


main()
