from typing import Dict, TYPE_CHECKING

import emoji
from requests import get

if TYPE_CHECKING:
    import telegram
    import telegram.ext


def ud(update: "telegram.Update", context: "telegram.ext.CallbackContext") -> None:
    """Query Urban Dictionary for word definition"""
    if update.message:
        message: "telegram.Message" = update.message
    else:
        return

    text: str
    word: str = " ".join(context.args) if context.args else ""

    if not word:
        text = "*Usage:* `/ud {QUERY}`\n*Example:* `/ud boomer`\n"
    else:
        result: Dict = get(
            f"http://api.urbandictionary.com/v0/define?term={word}"
        ).json()

        if result["list"]:
            # Sort to get result with most thumbs up
            result = max(result["list"], key=lambda x: x["thumbs_up"])

            text = (
                f"*{result['word']}*\n\n"
                f"{result['definition']}\n\n"
                f"_{result['example']}_\n\n"
                f"`{emoji.emojize(':thumbs_up:')} × {result['thumbs_up']}`"
            )
        else:
            text = "No entry found."

    message.reply_text(text=text)
