INSERT_COIN = '   WITH args (name, ticker) AS (VALUES (?, ?)) ' \
              'REPLACE INTO coin (id, name, ticker) ' \
              ' SELECT c.id, ' \
              '        (CASE WHEN c.name IS NULL THEN args.name ELSE c.name END), ' \
              '        (CASE WHEN c.ticker IS NULL THEN args.ticker ELSE c.ticker END) ' \
              '   FROM args ' \
              '   LEFT JOIN coin c ON c.name = args.name AND c.ticker = args.ticker;'

INSERT_USER = 'WITH args (telegram_username) AS (VALUES (?)) ' \
              'REPLACE INTO user(id, telegram_username) ' \
              ' SELECT u.id, ' \
              '        (CASE WHEN u.telegram_username IS NULL THEN args.telegram_username ELSE u.telegram_username END) ' \
              '   FROM args ' \
              '   LEFT JOIN user u ON u.telegram_username = args.telegram_username;'

SELECT_USER_ID_BY_TELEGRAM_USERNAME = 'SELECT id ' \
                                      '  FROM user ' \
                                      ' WHERE telegram_username = ?;'

UPDATE_USER_ACTIVITY = '   WITH args ( user_id, chat_id, activity_timestamp ) AS ( VALUES( ?, ?, ? ) ) ' \
                       'REPLACE INTO activity ( id, user_id, chat_id, activity_timestamp ) ' \
                       ' SELECT a.id AS id, ' \
                       '        ( CASE WHEN a.user_id IS NULL THEN args.user_id ELSE a.user_id END ), ' \
                       '        ( CASE WHEN a.chat_id IS NULL THEN args.chat_id ELSE a.chat_id END ), ' \
                       '        args.activity_timestamp ' \
                       '   FROM args ' \
                       '   LEFT JOIN activity AS a ON args.user_id = a.user_id AND args.chat_id = a.chat_id;'

SELECT_ALL_ACTIVITY_WITH_USERNAMES = 'SELECT u.telegram_username, a.chat_id, a.activity_timestamp ' \
                                     '  FROM activity a ' \
                                     '  LEFT JOIN user u ON u.id = a.user_id;'

UPDATE_USER_BALANCE = '   WITH args ( telegram_username, coin_ticker, off_chain_balance_amount  ) AS ( VALUES( ?, ?, ? ) ) ' \
                      'REPLACE INTO balance ( id, user_id, coin_id, off_chain_balance_amount ) ' \
                      ' SELECT b.id AS id, ' \
                      '        ( CASE WHEN b.user_id IS NULL THEN u.id ELSE b.user_id END ) AS user_id, ' \
                      '        ( CASE WHEN b.coin_id IS NULL THEN c.id ELSE b.coin_id END ) AS coin_id, ' \
                      '        ( ROUND((CASE WHEN b.off_chain_balance_amount IS NULL THEN 0 ELSE b.off_chain_balance_amount  END) + ' \
                      '             args.off_chain_balance_amount, 8)) ' \
                      '   FROM args, user u, coin c' \
                      '   LEFT JOIN balance b ON b.user_id = u.id' \
                      '  WHERE u.telegram_username = args.telegram_username ' \
                      '    AND c.ticker = args.coin_ticker;'

SELECT_USER_OFF_CHAIN_BALANCE = 'SELECT b.off_chain_balance_amount ' \
                                '  FROM balance b, user u ' \
                                ' WHERE u.telegram_username = ?' \
                                '   AND b.user_id = u.id;'
