#!/usr/bin/env python3
from typing import List
from app.entities import Task, Mark, MessageId, ChatId, KindOfTask

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
    def _get_task_markup(
        tasks: List[Task],
        is_state_delete=None,
    ) -> InlineKeyboardMarkup:
        tasks = sorted(tasks, key=lambda task: task.kind.value)
        keyboard = []
        for t in tasks:
            if is_state_delete:
                mark = Mark.DELETE
                callback_prefix = "delete:"
            elif t.kind == KindOfTask.TODO:
                mark = Mark.TODO
                callback_prefix = "todos:"
            else:
                mark = Mark.DONE if t.is_done else Mark.NOT_DONE
                callback_prefix = "habits:"

            keyboard.append([
                InlineKeyboardButton(
                    text=mark.value + t.name,
                    callback_data=callback_prefix + t.id,
                )
            ])
        if is_state_delete:
            keyboard.append([
                InlineKeyboardButton(
                    text="Back to list",
                    callback_data="back"
                )
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(
                    text="Delete Habit",
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

    def send_tasks(self, chat_id, tasks: List[Task]):
        markup = self._get_task_markup(tasks)
        return self._bot.send_message(
            chat_id=chat_id,
            text="*YOUR HABITS AND TODOS:*",
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

    def update_tasks(
        self,
        chat_id: ChatId,
        message_id: MessageId,
        tasks: List[Task],
        is_state_delete=False,
    ) -> None:
        markup = self._get_task_markup(tasks, is_state_delete)
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
