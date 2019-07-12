-- user table
CREATE TABLE IF NOT EXISTS telegram_user (
 id integer PRIMARY KEY,
 username text NOT NULL UNIQUE
);

-- activity table
CREATE TABLE IF NOT EXISTS activity (
 id integer PRIMARY KEY,
 user_id integer NOT NULL,
 chat_id integer NOT NULL,
 activity_timestamp integer NOT NULL,
 FOREIGN KEY (chat_id) REFERENCES telegram_chat (id),
 FOREIGN KEY (user_id) REFERENCES telegram_user (id)
);