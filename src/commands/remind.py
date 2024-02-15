import datetime

import dateparser
from telegram import (
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import commands
import utils
from config.db import sqlite_conn
from utils.decorators import description, example, triggers, usage


def readable_time(time: datetime.datetime) -> str:
    now = datetime.datetime.now()
    time_difference = time - now

    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Construct the string
    time_left = ""
    if days > 0:
        time_left += f"{days} days, "
    if hours > 0:
        time_left += f"{hours} hours, "
    if minutes > 0:
        time_left += f"{minutes} minutes"

    # Remove the trailing comma and space if present
    if time_left.endswith(", "):
        time_left = time_left[:-2]

    return time_left


def reminder_list(user_id: int, chat_id: int) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute(
        """
        SELECT id, title, target_time
        FROM reminders WHERE user_id = ? AND chat_id = ? AND target_time > STRFTIME('%s', 'now');
        """,
        (user_id, chat_id),
    )

    results = cursor.fetchall()
    text = "⏰ Your reminders in this chat:\n"

    for index, reminder in enumerate(results):
        parsed_time = datetime.datetime.fromtimestamp(reminder["target_time"])
        text += f'\n{index + 1}. <code>{reminder["title"]}</code> in {readable_time(parsed_time)}'

    return text


@triggers(["remind"])
@usage("/remind [REMINDER_NAME] [TARGET_TIME]")
@description("Create a reminder with a trigger time for this group.")
@example("/remind Japan Trip - 5 months later")
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a reminder with a trigger time for this group."""
    cursor = sqlite_conn.cursor()

    if not context.args:
        existing_reminders = cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM reminders WHERE user_id = ? AND chat_id = ? AND target_time > STRFTIME('%s', 'now');
            """,
            (update.message.from_user.id, update.message.chat_id),
        )

        existing_reminders = existing_reminders.fetchone()
        if existing_reminders["count"] > 0:
            await update.message.reply_text(
                text=reminder_list(update.message.from_user.id, update.message.chat_id),
                parse_mode=ParseMode.HTML,
            )
            return

        await commands.usage_string(update.message, remind)
        return

    command_args = (" ".join(context.args)).split("-")

    if len(command_args) < 2:
        await commands.usage_string(update.message, remind)
        return

    title, target_time = command_args[0], command_args[1]
    title = title.strip()
    target_time = target_time.strip()

    target_time = dateparser.parse(target_time)
    if target_time < datetime.datetime.now():
        await update.message.reply_text(text="Reminder time cannot be in the past.")
        return

    cursor.execute(
        """
        INSERT INTO reminders (chat_id, user_id, title, target_time)
        VALUES (?, ?, ?, ?);
        """,
        (
            update.message.chat_id,
            update.message.from_user.id,
            title,
            target_time.timestamp(),
        ),
    )

    await update.message.reply_text(
        text=f'I will remind you about <code>{title}</code> on {target_time.strftime("%B %d, %Y at %I:%M%p")}',
        parse_mode=ParseMode.HTML,
    )


async def worker_reminder(context: ContextTypes.DEFAULT_TYPE):
    cursor = sqlite_conn.cursor()
    existing_reminders = cursor.execute(
        """
        SELECT id, title, target_time, user_id, chat_id
        FROM reminders 
        WHERE target_time > STRFTIME('%s', 'now') 
        AND target_time <= STRFTIME('%s', 'now', '+5 minutes');
        """,
    )

    existing_reminders = existing_reminders.fetchall()
    for reminder in existing_reminders:
        text = f'⏰ <code>{reminder["title"]}</code>\n\n@{await utils.get_username(reminder["user_id"], context)}'
        await context.bot.send_message(
            reminder["chat_id"], text, parse_mode=ParseMode.HTML
        )
