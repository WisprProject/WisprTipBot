class Command:
    activity_tracker = None
    command_to_run = None
    coin_properties = None

    def __init__( self, command_to_run, coin_properties, activity_tracker = None ):
        self.activity_tracker = activity_tracker
        self.command_to_run = command_to_run
        self.coin_properties = coin_properties

    def __call__( self, bot, update ):
        if self.activity_tracker is not None:
            self.activity_tracker.track_activity( bot, update )

        command_message = self.command_to_run( update, self.coin_properties )

        bot.send_message( chat_id = update.message.chat_id, text = command_message )
