import logging

from logic.common import messages
from logic.common.botusererror import BotUserError
from logic.model.coinproperties import CoinProperties

logger = logging.getLogger( __name__ )


class Command:
    activity_tracker = None
    command_to_run = None
    coin_properties = None

    def __init__( self, command_to_run, coin_properties: CoinProperties, activity_tracker = None ):
        self.activity_tracker = activity_tracker
        self.command_to_run = command_to_run
        self.coin_properties = coin_properties

    def __call__( self, bot, update ):
        if self.activity_tracker is not None:
            self.activity_tracker.track_activity( bot, update )

        try:
            message, *parse_mode = self.command_to_run( update, self.coin_properties )

            if len( parse_mode ) is 0:
                bot.send_message( chat_id = update.message.chat_id, text = message )
            else:
                bot.send_message( chat_id = update.message.chat_id, text = message, parse_mode = parse_mode[ 0 ], disable_web_page_preview = True )
        except BotUserError as e:
            bot.send_message( chat_id = update.message.chat_id, text = e.message )
        except Exception as e:
            logger.exception( "message" )
            bot.send_message( chat_id = update.message.chat_id, text = messages.GENERIC_ERROR )
