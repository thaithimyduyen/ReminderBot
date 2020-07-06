#!/usr/bin/env python3
import logging
import redis

from telegram import Bot
from telegram.utils.request import Request
from telegram.ext import Updater

from app.remindercontroll import ReminderBotCotroller
from app.remindermodel import ReminderBotModel
from app.reminderview import ReminderBotViewer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


class ReminderBot:
    def __init__(
        self,
        token: str,
        state_file=".state.dat"
    ):
        req = Request(con_pool_size=8)
        bot = Bot(token=token, request=req)

        kv = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
        )
        self._updater = Updater(
            bot=bot,
            use_context=True,
        )
        self._view = ReminderBotViewer(bot=bot)
        self._model = ReminderBotModel(
            view=self._view,
            bot=bot,
            kv=kv
        )
        self._controller = ReminderBotCotroller(self._model, self._updater)

    def run(self) -> None:
        self._updater.start_polling()
