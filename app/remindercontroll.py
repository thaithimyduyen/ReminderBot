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
        self._model.add_tasks(update, context)

    def _handle_button_clicked(
        self,
        update: Update,
        context: CallbackContext,
    ) -> None:
        query_data = update.callback_query.data
        if query_data.startswith("habits:"):
            self._model.mark_habit(
                update=update,
                context=context,
                habit_id=trim_prefix(query_data, "habits:")
            )
        elif query_data.startswith("todos:"):
            self._model.complete_todo(
                update=update,
                context=context,
                todo_id=trim_prefix(query_data, "todos:")
            )
        elif query_data.startswith("delete:"):
            self._model.delete_task(
                update=update,
                context=context,
                task_id=trim_prefix(query_data, "delete:")
            )
        elif query_data == "delete mode":
            self._model.delete_mode(
                update=update,
                context=context,
            )
        elif query_data == "back":
            self._model.normal_mode(
                update=update,
                context=context,
            )


def trim_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]
