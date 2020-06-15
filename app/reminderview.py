#!/usr/bin/env python3
from typing import List
from app.entities import Habit, Mark, MessageId, ChatId

from telegram import (
    ParseMode,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
CUSTOM_KEYBOARD = [
    ["/start"]
]


class ReminderBotViewer:
    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    def _get_habit_markup(
        habits: List[Habit],
        is_state_delete=None,
    ) -> InlineKeyboardMarkup:
        keyboard = []
        for h in habits:
            mark = Mark.DONE if h.is_done else Mark.NOT_DONE
            callback_prefix = "habits:"

            if is_state_delete:
                mark = Mark.DELETE
                callback_prefix = "delete:"

            keyboard.append([
                InlineKeyboardButton(
                    text=mark.value + h.name,
                    callback_data=callback_prefix + h.id,
                )
            ])
        if is_state_delete:
            keyboard.append([
                InlineKeyboardButton(
                    text="Back to list of habits",
                    callback_data="back"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    text="Delete Habbit",
                    callback_data="delete mode"
                )
            ])
        return InlineKeyboardMarkup(keyboard)

    def send_message_reply(
        self,
        chat_id,
        text,
        message_id,
    ) -> None:
        reply_markup = ReplyKeyboardMarkup(
            CUSTOM_KEYBOARD, resize_keyboard=True)
        self._bot.send_message(
            reply_to_message_id=message_id,
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )

    def send_habits(self, chat_id, habits: List[Habit]):
        markup = self._get_habit_markup(habits)
        return self._bot.send_message(
            chat_id=chat_id,
            text="*YOUR HABBITS:*",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        ).message_id

    def send_message(self, chat_id, text) -> None:
        reply_markup = ReplyKeyboardMarkup(
            CUSTOM_KEYBOARD, resize_keyboard=True)
        self._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    def send_sticker(self, chat_id, sticker) -> None:
        self._bot.send_sticker(
            chat_id=chat_id,
            sticker=sticker
        )

    def update_habits(
        self,
        chat_id: ChatId,
        message_id: MessageId,
        habits: List[Habit],
        is_state_delete=False,
    ) -> None:
        markup = self._get_habit_markup(habits, is_state_delete)
        self._bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
        )

    def show_expired(
        self,
        chat_id: ChatId,
        message_id: MessageId,
    ) -> None:
        self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="The message is expired\nSend /start",
        )
