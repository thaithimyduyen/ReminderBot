#!/usr/bin/env python3
from telegram import Update, Bot
from telegram.ext import CallbackContext

from app.reminderview import ReminderBotViewer
from app.entities import Habit, StateHabit

KEY_USER_HABBITS = "habits"


class ReminderBotModel:
    def __init__(self, view: ReminderBotViewer, bot: Bot):
        self._view = view
        self._bot = bot

    def start(self, update: Update, context: CallbackContext):
        self._view.send_message(
            chat_id=update.effective_message.chat_id,
            context=context,
            text="Add your habits!!"
        )

    def add_habits(self, update: Update, context: CallbackContext) -> None:
        habits_inp = update.effective_message.text.split("\n")
        if KEY_USER_HABBITS not in context.user_data:
            context.user_data[KEY_USER_HABBITS] = []

        habits = context.user_data[KEY_USER_HABBITS]

        unique_habit_names = set()
        for h in habits:
            unique_habit_names.add(h.name)

        for h in habits_inp:
            if h in unique_habit_names:
                continue
            unique_habit_names.add(h)
            habits.append(Habit(h))

        self.show_habits(update, context)

    def show_habits(self, update: Update, context: CallbackContext) -> None:
        habits = context.user_data[KEY_USER_HABBITS]
        self._view.send_habits(update.effective_message.chat_id, habits)

    def mark_habits(
        self,
        update: Update,
        context: CallbackContext,
        habit_id: int,
    ) -> None:
        habits = context.user_data[KEY_USER_HABBITS]
        habits[habit_id].state = StateHabit.DONE
        self._view.update_habit(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            habits=habits
        )
