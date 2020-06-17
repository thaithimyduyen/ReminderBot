#!/usr/bin/env python3

import datetime

from typing import List
from telegram import Update, Bot
from telegram.ext import CallbackContext

from app.reminderview import ReminderBotViewer
from app.entities import Task, KindOfTask


TODO_PREFIX = "#TODO "

DAYS_OF_THE_WEEK = 7
FILE_STICKER = "assets/sticker.webp"

KEY_USER_TASKS = "habits"
KEY_LAST_START_DATE = "last_date_start"
KEY_WEEK_SCORE = "week_score"
KEY_LAST_YEAR_WEEK = "number_week_year"


class ReminderBotModel:
    def __init__(self, view: ReminderBotViewer, bot: Bot):
        self._view = view
        self._bot = bot

    @staticmethod
    def _tasks(context: CallbackContext) -> List[Task]:
        if KEY_USER_TASKS not in context.user_data:
            context.user_data[KEY_USER_TASKS] = []

        return context.user_data[KEY_USER_TASKS]

    def start(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        current_time_start = datetime.datetime.utcnow().date()

        if KEY_LAST_START_DATE not in context.user_data:
            self._view.send_message(
                chat_id=chat_id,
                text="Welcome to the Reminder Bot!\n\n" +
                "You can add your habits and todo tasks whenever you want" +
                " by sending to the bot a simple message.\n\n"
                "Command /start for getting a list of your tasks\n\n" +
                "For creating a TODO task put #TODO at the beginning " +
                "of the task message."
            )
            context.user_data[KEY_LAST_START_DATE] = current_time_start
            return

        last_start_time = context.user_data.get(
            KEY_LAST_START_DATE, current_time_start
        )
        context.user_data[KEY_LAST_START_DATE] = current_time_start
        if current_time_start != last_start_time:
            self._handle_stats_habits(update, context)

        tasks = self._tasks(context)

        if len(tasks) == 0:
            self._view.send_message(
                chat_id=chat_id,
                text="Add your tasks!!"
            )
            return

        self._show_tasks(update, context)

    def _handle_stats_habits(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        tasks = self._tasks(context)
        habits = list(filter(lambda h: h.kind ==
                             KindOfTask.HABIT, tasks))
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        count_done_habits = sum(
            1 for h in habits if h.done_date == yesterday.date()
        )
        precent_done = round(count_done_habits*100/len(habits))
        text = f"Yesterday you completed {precent_done}% of your habits"

        if KEY_WEEK_SCORE not in context.user_data:
            context.user_data[KEY_WEEK_SCORE] = 0

        current_year_week = yesterday.isocalendar()[:2]
        last_year_week = context.user_data.get(
            KEY_LAST_YEAR_WEEK, current_year_week
        )
        if last_year_week == current_year_week:
            context.user_data[KEY_WEEK_SCORE] += precent_done
        else:
            score = round(context.user_data[KEY_WEEK_SCORE] / DAYS_OF_THE_WEEK)
            text += f"Your last week score is {score}"
            context.user_data[KEY_WEEK_SCORE] = 0

        context.user_data[KEY_LAST_YEAR_WEEK] = current_year_week

        self._view.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
        )

    def add_tasks(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        tasks = self._tasks(context)

        tasks_inp = update.effective_message.text.splitlines()

        unique_task_names = set()
        for h in tasks:
            unique_task_names.add(h.name)

        for h in tasks_inp:
            if h in unique_task_names:
                continue
            task = Task(h)
            if h.upper().startswith(TODO_PREFIX):
                task.kind = KindOfTask.TODO
                task.name = h[len(TODO_PREFIX):]
                if len(task.name.strip()) == 0:
                    continue

            unique_task_names.add(h)
            tasks.append(task)

        self._show_tasks(update, context)

    def _show_tasks(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        tasks = self._tasks(context)
        self._view.send_tasks(
            update.effective_message.chat_id, tasks)

    def normal_mode(self, update: Update, context: CallbackContext) -> None:
        tasks = self._tasks(context)
        self._view.update_tasks(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            tasks=tasks
        )

    def delete_mode(self, update: Update, context: CallbackContext) -> None:
        tasks = self._tasks(context)
        self._view.update_tasks(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            tasks=tasks,
            is_state_delete=True,
        )

    def complete_todo(
        self,
        update: Update,
        context: CallbackContext,
        todo_id: str
    ) -> None:
        tasks = self._tasks(context)
        for (i, h) in enumerate(tasks):
            if h.id == todo_id:
                del tasks[i]
        self._view.update_tasks(
            chat_id=update.effective_message.chat_id,
            message_id=update.effective_message.message_id,
            tasks=tasks,
        )

    def delete_task(
        self,
        update: Update,
        context: CallbackContext,
        task_id: str,
    ) -> None:
        tasks = self._tasks(context)
        for (i, h) in enumerate(tasks):
            if h.id == task_id:
                del tasks[i]
        self.delete_mode(update, context)

    def mark_habit(
        self,
        update: Update,
        context: CallbackContext,
        habit_id: str,
    ) -> None:
        chat_id = update.effective_message.chat_id
        message_id = update.effective_message.message_id
        tasks = self._tasks(context)
        habits = list(filter(lambda h: h.kind ==
                             KindOfTask.HABIT, tasks))

        time_sent_msg = update.effective_message.date.date()
        if time_sent_msg != datetime.datetime.utcnow().date():
            self._view.show_expired(
                chat_id=chat_id,
                message_id=message_id,
            )
            return

        count_done_habits = 0
        for h in habits:
            if h.id == habit_id:
                h.is_done ^= True
            if h.is_done:
                count_done_habits += 1

        if count_done_habits == len(habits):
            with open(FILE_STICKER, 'rb') as f:
                self._view.send_sticker(
                    chat_id=chat_id,
                    sticker=f,
                )

        self._view.update_tasks(
            chat_id=chat_id,
            message_id=message_id,
            tasks=tasks,
        )
