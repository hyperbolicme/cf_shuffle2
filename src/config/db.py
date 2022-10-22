import os
import sqlite3

import redis


def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


sqlite_conn = sqlite3.connect(
    f"{os.getcwd() if not is_docker() else '/db'}/SuperSeriousBot.db",
    check_same_thread=False,
    isolation_level=None,
)

sqlite_conn_law_database = sqlite3.connect(
    f"{os.getcwd() if not is_docker() else '/db'}/IndiaLaw.db",
    check_same_thread=False,
    isolation_level=None,
)

sqlite_conn.row_factory = sqlite3.Row
sqlite_conn_law_database.row_factory = sqlite3.Row

redis = redis.StrictRedis(
    host=f"{'redis' if is_docker() else '127.0.0.1'}",
    port=6379,
    db=0,
    decode_responses=True,
    charset="utf-8",
)

cursor = sqlite_conn.cursor()

# Chat Statistics Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat_mentions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        mentioning_user_id INTEGER NOT NULL,
        mentioned_user_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL
    )
    """
)

# Bot command statistics table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS command_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command VARCHAR(255) NOT NULL,
        user_id INTEGER NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)

# Table for TV Show Notifications
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `tv_opt_in` (
        `id` INTEGER PRIMARY KEY,
        `user_id` INTEGER NOT NULL,
        `chat_id` VARCHAR(255) NOT NULL,
        `username` VARCHAR(255) NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `tv_notifications` (
        `id` INTEGER PRIMARY KEY,
        `user_id` SIGNED INTEGER NOT NULL,
        `show_id` VARCHAR(255) NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `tv_shows` (
        `id` INTEGER PRIMARY KEY,
        `show_id` VARCHAR(255) NOT NULL,
        `show_name` VARCHAR(255) NOT NULL,
        `show_image` VARCHAR(255) NOT NULL,
        `next_episode_time` INTEGER NULL,
        `next_episode_name` VARCHAR(255) NULL,
        `sent` INTEGER NOT NULL DEFAULT 0,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

# Table for Reddit Subscriptions
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `reddit_subscriptions` (
        `id` INTEGER PRIMARY KEY,
        `group_id` INTEGER NOT NULL,
        `subreddit_name` VARCHAR(255) NOT NULL,
        `receiver_id` INTEGER NOT NULL,
        `receiver_username` VARCHAR(255) NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

# Table for object store
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `object_store` (
        `id` INTEGER PRIMARY KEY,
        `file_id` VARCHAR(255) NOT NULL,
        `file_unique_id` VARCHAR(255) NOT NULL,
        `key` VARCHAR(255) NOT NULL UNIQUE,
        `user_id` INTEGER NOT NULL,
        `type` VARCHAR(255) NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

# Table for Quote DB
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `quote_db` (
        `id` INTEGER PRIMARY KEY,
        `message_id` INTEGER NOT NULL,
        `chat_id` INTEGER NOT NULL,
        `message_user_id` INTEGER NOT NULL,
        `saver_user_id` INTEGER NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

# Table for Summon Groups
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `summon_groups` (
        `id` INTEGER PRIMARY KEY,
        `chat_id` INTEGER NOT NULL,
        `group_name` VARCHAR(255) NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `creator_id` INTEGER NOT NULL
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `summon_group_members` (
        `id` INTEGER PRIMARY KEY,
        `group_id` INTEGER NOT NULL,
        `user_id` INTEGER NOT NULL,
        `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
)

# Add some indexes
cursor.execute(
    "CREATE INDEX IF NOT EXISTS chat_stats_chat_id_user_id_index ON chat_stats (chat_id, user_id);"
)
cursor.execute(
    "CREATE INDEX IF NOT EXISTS command_stats_user_id_command_index ON command_stats (command, user_id);"
)
cursor.execute(
    "CREATE INDEX IF NOT EXISTS tv_opt_in_user_id_chat_id_index ON tv_opt_in (user_id, chat_id);"
)
cursor.execute(
    "CREATE INDEX IF NOT EXISTS summon_groups_group_name_index ON summon_groups (group_name);"
)
