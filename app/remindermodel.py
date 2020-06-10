#!/usr/bin/env python3
from telegram import Update, Bot
from telegram.ext import CallbackContext

from app.reminderview import ReminderBotViewer
from app.entities import Habbit

KEY_USER_HABBITS = "habbits"


class ReminderBotModel:
    def __init__(self, view: ReminderBotViewer, bot: Bot):
        self._view = view
        self._bot = bot

    def start(self, update: Update, context: CallbackContext):
        self._view.send_message(
            chat_id=update.effective_message.chat_id,
            context=context,
            text="Add your habbits!!"
        )

    def add_habbits(self, update: Update, context: CallbackContext) -> None:
        habbits_inp = update.effective_message.text.split("\n")
        if KEY_USER_HABBITS not in context.user_data:
            context.user_data[KEY_USER_HABBITS] = []
        for h in habbits_inp:
            habbit = Habbit(h)
            context.user_data[KEY_USER_HABBITS].append(habbit)
        self.show_habbits(update, context)

    def show_habbits(self, update: Update, context: CallbackContext) -> None:
        habbits = context.user_data[KEY_USER_HABBITS]
        self._view.send_habbits(update.effective_message.chat_id, habbits)

    def mark_habbits(self, update: Update, context: CallbackContext):
        pass
