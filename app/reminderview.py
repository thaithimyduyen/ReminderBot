#!/usr/bin/env python3
from typing import List
from app.entities import Habbit

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
    def _get_habbit_markup(habbits: List[Habbit]):
        keyboard = []
        for habbit in habbits:
            keyboard.append([
                InlineKeyboardButton(
                    text=habbit.name,
                    callback_data="habbit"
                )]
            )
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

    def send_habbits(self, chat_id, habbits: List[Habbit]):
        markup = self._get_habbit_markup(habbits)
        return self._bot.send_message(
            chat_id=chat_id,
            text="*YOUR HABBITS:*",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        ).message_id

    def send_message(self, chat_id, context, text) -> None:
        reply_markup = ReplyKeyboardMarkup(
            CUSTOM_KEYBOARD, resize_keyboard=True)
        self._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
