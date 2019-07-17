import logging

from logic.botusererror import BotUserError
from db import database
from db import statements
from datetime import datetime
from logic.helpers import commonhelper
from logic.helpers.configuration import Configuration


class ActivityTracker:
    active_users_cache = None

    def __init__( self ):
        connection = database.create_connection()

        with connection:
            active_users = database.fetch_result( connection, statements.SELECT_ALL_ACTIVITY_WITH_USERNAMES )
            logging.debug( f'Active users fetched.' )

            if self.active_users_cache is None and active_users is not None:
                self.active_users_cache = { }
                for active_user in active_users:
                    user_id = active_user[ 0 ]
                    chat_id = active_user[ 1 ]
                    activity_timestamp = active_user[ 2 ]
                    if chat_id not in self.active_users_cache:
                        self.active_users_cache.update( { chat_id: { user_id: activity_timestamp } } )
                    else:
                        self.active_users_cache[ chat_id ].update( { user_id: activity_timestamp } )

                logging.info( 'Active users cache loaded.' )

    def track_activity( self, bot, update ):
        try:
            chat_id = update.message.chat_id
            now = datetime.now()
            current_time = datetime.timestamp( now )
            user = commonhelper.get_username( update )
            connection = database.create_connection()

            with connection:
                user_id = database.fetch_result( connection, statements.SELECT_TELEGRAM_USER_ID_BY_NAME, (user,) )

                if user_id is None:
                    user_id = database.execute_query( connection, statements.INSERT_TELEGRAM_USER, (user,) )

                database.execute_query( connection, statements.UPDATE_USER_ACTIVITY, (user_id, chat_id, current_time,) )

            if chat_id not in self.active_users_cache:
                self.active_users_cache.update( { chat_id: { user: current_time } } )
            else:
                if user not in self.active_users_cache[ chat_id ]:
                    self.active_users_cache[ chat_id ].update( { user: current_time } )
                else:
                    self.active_users_cache[ chat_id ][ user ] = current_time

            logging.info( f'@{user} spoke @{chat_id} at {self.active_users_cache[ chat_id ][ user ]}.' )
        except BotUserError as e:
            logging.info( e )

    def get_current_active_users( self, update, user ):
        eligible_users = [ ]
        chat_id = update.message.chat_id

        if self.active_users_cache is not None and self.active_users_cache[ chat_id ] is not None:
            for active_user in self.active_users_cache[ chat_id ]:
                now = datetime.now()
                current_time = datetime.timestamp( now )

                if current_time - self.active_users_cache[ chat_id ][ active_user ] <= Configuration.CHAT_ACTIVITY_TIME \
                        and active_user != user:
                    eligible_users.append( active_user )

        if len( eligible_users ) is 0:
            logging.info( f'No eligible users for receiving rain in chatId: {chat_id} '
                         f'found from active users: {self.active_users_cache}' )

        return eligible_users
