class Command:
    activity_tracker = None
    command_to_run = None

    def __init__( self, command_to_run, activity_tracker=None ):
        self.activity_tracker = activity_tracker
        self.command_to_run = command_to_run

    def run( self, bot, update ):
        if self.activity_tracker is not None:
            self.activity_tracker.track_activity( bot, update )

        return self.command_to_run( bot, update )
