#!/usr/bin/env python3
from typing import List
from app.entities import Habit, Mark, StateHabit, MessageId, ChatId

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
    def _get_habit_markup(habits: List[Habit]):
        keyboard = []
        for h in habits:
            mark = Mark.DONE if h.state == StateHabit.DONE else Mark.NOT_DONE
            keyboard.append([
                InlineKeyboardButton(
                    text=mark.value + h.name,
                    callback_data="habits:"+str(habits.index(h))
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

    def send_habits(self, chat_id, habits: List[Habit]):
        markup = self._get_habit_markup(habits)
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

    def update_habit(
        self,
        chat_id: ChatId,
        message_id: MessageId,
        habits: List[Habit]
    ) -> None:
        markup = self._get_habit_markup(habits)
        self._bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
        )
