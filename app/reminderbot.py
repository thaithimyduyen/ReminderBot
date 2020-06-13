#!/usr/bin/env python3
import logging

from telegram import Bot
from telegram.utils.request import Request
from telegram.ext import Updater, PicklePersistence

from app.remindercontroll import ReminderBotCotroller
from app.remindermodel import ReminderBotModel
from app.reminderview import ReminderBotViewer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class ReminderBot:
    def __init__(
        self,
        token: str,
        proxy_url: str = "socks5://127.0.0.1:9050",
        state_file=".state.dat"
    ):
        req = Request(proxy_url=proxy_url, con_pool_size=8)
        bot = Bot(token=token, request=req)

        self._persistence = PicklePersistence(filename=state_file)
        self._updater = Updater(
            bot=bot,
            use_context=True,
            persistence=self._persistence,
        )
        self._view = ReminderBotViewer(bot=bot)
        self._model = ReminderBotModel(
            view=self._view,
            bot=bot,
        )
        self._controller = ReminderBotCotroller(self._model, self._updater)

    def run(self) -> None:
        self._updater.start_polling()

    def flush(self) -> None:
        self._persistence.flush()
