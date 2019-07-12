INSERT_TELEGRAM_USER = 'REPLACE INTO telegram_user( username ) VALUES( ? );'

SELECT_TELEGRAM_USER_ID_BY_NAME = 'SELECT id FROM telegram_user WHERE username = ?;'

UPDATE_USER_ACTIVITY = 'WITH new ( user_id, chat_id, activity_timestamp ) AS ( VALUES( ?, ?, ?) ) ' \
                       'REPLACE INTO activity ( id, user_id, chat_id, activity_timestamp ) ' \
                       'SELECT old.id AS id, ' \
                               '( CASE WHEN old.user_id IS NULL then new.user_id ELSE old.user_id END ) AS user_id, ' \
                               '( CASE WHEN old.chat_id IS NULL then new.chat_id ELSE old.chat_id END ) AS chat_id, ' \
                               'new.activity_timestamp ' \
                       'FROM new ' \
                       'LEFT JOIN activity AS old ON new.user_id = old.user_id AND new.chat_id = old.chat_id;'

SELECT_ALL_ACTIVITY_WITH_USERNAMES = 'SELECT tu.username, a.chat_id, a.activity_timestamp ' \
                                     'FROM activity a ' \
                                     'LEFT JOIN telegram_user tu ON tu.id = a.user_id;'
