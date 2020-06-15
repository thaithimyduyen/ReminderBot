#!/usr/bin/env python3

import datetime

from typing import List
from telegram import Update, Bot
from telegram.ext import CallbackContext

from app.reminderview import ReminderBotViewer
from app.entities import Habit

KEY_USER_HABBITS = "habits"


class ReminderBotModel:
    def __init__(self, view: ReminderBotViewer, bot: Bot):
        self._view = view
        self._bot = bot

    @staticmethod
    def _habits(context: CallbackContext) -> List[Habit]:
        if KEY_USER_HABBITS not in context.user_data:
            context.user_data[KEY_USER_HABBITS] = []

        return context.user_data[KEY_USER_HABBITS]

    def start(self, update: Update, context: CallbackContext) -> None:
        habits = self._habits(context)

        if len(habits) == 0:
            self._view.send_message(
                chat_id=update.effective_message.chat_id,
                context=context,
                text="Add your habits!!"
            )
            return

        self._show_habits(update, context)

    def add_habits(self, update: Update, context: CallbackContext) -> None:
        habits = self._habits(context)

        habits_inp = update.effective_message.text.splitlines()

        unique_habit_names = set()
        for h in habits:
            unique_habit_names.add(h.name)

        for h in habits_inp:
            if h in unique_habit_names:
                continue
            unique_habit_names.add(h)
            habits.append(Habit(h))

        self._show_habits(update, context)

    def _show_habits(self, update: Update, context: CallbackContext) -> None:
        habits = self._habits(context)
        self._view.send_habits(update.effective_message.chat_id, habits)

    def normal_mode(self, update: Update, context: CallbackContext) -> None:
        habits = self._habits(context)
        self._view.update_habit(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            habits=habits
        )

    def delete_mode(self, update: Update, context: CallbackContext) -> None:
        habits = self._habits(context)
        self._view.update_habit(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            habits=habits,
            is_state_delete=True,
        )

    def delete_habit(
        self,
        update: Update,
        context: CallbackContext,
        habit_id: str,
    ) -> None:
        habits = self._habits(context)
        for (i, h) in enumerate(habits):
            if h.id == habit_id:
                del habits[i]
        self.delete_mode(update, context)

    def mark_habit(
        self,
        update: Update,
        context: CallbackContext,
        habit_id: str,
    ) -> None:
        chat_id = update.effective_message.chat_id
        message_id = update.effective_message.message_id
        habits = self._habits(context)

        time_sent_msg = update.effective_message.date.date()
        if time_sent_msg != datetime.datetime.utcnow().date():
            self._view.show_expired(
                chat_id=chat_id,
                message_id=message_id,
            )
            return

        for h in habits:
            if h.id == habit_id:
                h.is_done ^= True

        self._view.update_habits(
            chat_id=chat_id,
            message_id=message_id,
            habits=habits,
        )
