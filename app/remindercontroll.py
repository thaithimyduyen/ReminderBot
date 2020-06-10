#!/usr/bin/env python3
from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Updater,
    Filters
)

from app.remindermodel import ReminderBotModel


class ReminderBotCotroller:
    def __init__(self, model: ReminderBotModel, updater: Updater):
        self._model = model

        updater.dispatcher.add_handler(
            CommandHandler('start', self._handle_start)
        )
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & (~Filters.command),
                self._handle_text
            )
        )
        updater.dispatcher.add_handler(
            CallbackQueryHandler(
                self._handle_button_clicked,
            )
        )

    def _handle_start(self, update: Update, context: CallbackContext) -> None:
        self._model.start(update, context)

    def _handle_text(self, update: Update, context: CallbackContext) -> None:
        self._model.add_habbits(update, context)

    def _handle_button_clicked(
        self,
        update: Update,
        context: CallbackContext,
    ) -> None:
        query_data = update.callback_query.data
        if query_data == "habit":
            self._model.mark_habbit(update, context)
