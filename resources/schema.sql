-- user table
CREATE TABLE IF NOT EXISTS user
(
    id                integer PRIMARY KEY,
    telegram_username text NOT NULL UNIQUE
);

-- coin table
CREATE TABLE IF NOT EXISTS coin
(
    id     integer PRIMARY KEY,
    name   text NOT NULL UNIQUE,
    ticker text NOT NULL UNIQUE
);

-- activity table
CREATE TABLE IF NOT EXISTS activity
(
    id                 integer PRIMARY KEY,
    user_id            integer NOT NULL,
    chat_id            integer NOT NULL,
    activity_timestamp integer NOT NULL,
    FOREIGN KEY (user_id) REFERENCES telegram_user (id)
);

-- balance table
CREATE TABLE IF NOT EXISTS balance
(
    id                       integer PRIMARY KEY,
    user_id                  integer NOT NULL,
    coin_id                  integer NOT NULL,
    off_chain_balance_amount decimal(10, 8),
    FOREIGN KEY (user_id) REFERENCES telegram_user (id),
    FOREIGN KEY (coin_id) REFERENCES coin (id)
);