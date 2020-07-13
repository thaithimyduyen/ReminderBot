#!/usr/bin/env python3

import datetime
import redis

from typing import List
from telegram import Update, Bot
from telegram.ext import CallbackContext

from app.reminderview import ReminderBotViewer
from app.entities import Task, KindOfTask, ChatId
from app.repository import TaskRepository

TODO_PREFIX = "#TODO "

DAYS_OF_THE_WEEK = 7
FILE_STICKER = "assets/sticker.webp"

KEY_USER_TASKS = "habits"
KEY_LAST_START_DATE = "last_date_start"


class ReminderBotModel:
    def __init__(self, view: ReminderBotViewer, bot: Bot, kv: redis.Redis):
        self._view = view
        self._bot = bot
        self._task_repository = TaskRepository(kv)

    def _tasks_by_callback(self, update: Update) -> List[Task]:
        user_id = update.callback_query.from_user.id
        return self._task_repository.get_all(user_id)

    def _tasks_by_message(self, update: Update) -> List[Task]:
        user_id = update.effective_message.from_user.id
        return self._task_repository.get_all(user_id)

    def start(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat_id
        user_id = update.effective_message.from_user.id
        current_time_start = datetime.datetime.utcnow().strftime("%d/%m/%y")

        if self._task_repository.get_last_start(user_id) == "":
            self._view.send_message(
                chat_id=chat_id,
                text="Welcome to the Reminder Bot!\n\n" +
                "You can add your habits and todo tasks whenever you want" +
                " by sending to the bot a simple message.\n\n"
                "Command /start for getting a list of your tasks\n\n" +
                "For creating a TODO task put #TODO at the beginning " +
                "of the task message."
            )
            self._task_repository.set_last_start(user_id, current_time_start)
            return

        last_start_time = self._task_repository.get_last_start(user_id)

        self._task_repository.set_last_start(user_id, current_time_start)
        if current_time_start != last_start_time:
            self._handle_stats_habits(update, context)

        tasks = self._tasks_by_message(update)

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
        tasks = self._tasks_by_message(update)
        habits = list(filter(lambda h: h.kind ==
                             KindOfTask.HABIT, tasks))
        if len(habits) == 0:
            return
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        count_done_habits = sum(
            1 for h in habits if h.done_date == yesterday.date()
        )
        precent_done = round(count_done_habits*100/len(habits))
        text = f"Yesterday you completed {precent_done}% of your habits"

        self._view.send_message(
            chat_id=update.effective_message.chat_id,
            text=text,
        )

    def add_tasks(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        user_id = update.effective_message.from_user.id

        tasks_inp = update.effective_message.text.splitlines()

        for h in tasks_inp:
            task = Task(h)
            if h.upper().startswith(TODO_PREFIX):
                task.kind = KindOfTask.TODO
                task.name = h[len(TODO_PREFIX):]
                if len(task.name.strip()) == 0:
                    continue

            self._task_repository.add(task, user_id)

        self._show_tasks(update, context)

    def _show_tasks(
        self,
        update: Update,
        context: CallbackContext
    ) -> None:
        tasks = self._tasks_by_message(update)
        self._view.send_tasks(
            update.effective_message.chat_id, tasks)

    def check_all_habits_done(
        self,
        tasks: List[Task],
        chat_id: ChatId
    ) -> None:
        habits = list(filter(lambda h: h.kind ==
                             KindOfTask.HABIT, tasks))
        count_done_habits = 0
        for h in habits:
            if h.is_done:
                count_done_habits += 1
        if count_done_habits == len(habits):
            with open(FILE_STICKER, 'rb') as f:
                self._view.send_sticker(
                    chat_id=chat_id,
                    sticker=f,
                )

    def normal_mode(self, update: Update, context: CallbackContext) -> None:
        tasks = self._tasks_by_callback(update)
        chat_id = update.effective_message.chat_id
        self.check_all_habits_done(tasks, chat_id)
        self._view.update_tasks(
            chat_id=chat_id,
            message_id=update.effective_message.message_id,
            tasks=tasks
        )

    def delete_mode(self, update: Update, context: CallbackContext) -> None:
        tasks = self._tasks_by_callback(update)

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
        user_id = update.callback_query.from_user.id
        tasks = self._tasks_by_callback(update)

        for task in tasks:
            if task.id == todo_id:
                self._task_repository.delete(user_id, task)
        tasks = self._tasks_by_callback(update)

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
        user_id = update.callback_query.from_user.id
        tasks = self._tasks_by_callback(update)
        for task in tasks:
            if task.id == task_id:
                self._task_repository.delete(user_id, task)
        self.delete_mode(update, context)

    def mark_habit(
        self,
        update: Update,
        context: CallbackContext,
        habit_id: str,
    ) -> None:
        chat_id = update.effective_message.chat_id
        message_id = update.effective_message.message_id
        user_id = update.callback_query.from_user.id

        tasks = self._tasks_by_callback(update)
        habits = list(filter(lambda h: h.kind ==
                             KindOfTask.HABIT, tasks))

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
                self._task_repository.add(h, user_id)

        tasks = self._tasks_by_callback(update)
        self.check_all_habits_done(tasks, chat_id)
        self._view.update_tasks(
            chat_id=chat_id,
            message_id=message_id,
            tasks=tasks,
        )
