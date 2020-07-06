#!/usr/bin/env python3
import enum
import uuid
import datetime

from dataclasses import dataclass
from dataclasses_json import dataclass_json

MessageId = str
ChatId = str
UserId = int


class LevelHabit(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Mark(enum.Enum):
    DONE = "✅ "
    NOT_DONE = "⬜ "
    DELETE = "🗑 "
    TODO = "📝 "


class KindOfTask(enum.Enum):
    HABIT = "habit"
    TODO = "todo"


@dataclass_json
@dataclass
class Task:
    kind: KindOfTask
    name: str
    id: str
    __done_time: datetime.datetime

    def __init__(
        self,
        name,
        id=None,
        kind=KindOfTask.HABIT,
        __done_time: datetime.datetime = datetime.datetime.fromtimestamp(0),
    ):
        self.kind = kind
        self.name = name
        if id is None:
            id = str(uuid.uuid1())
        self.id = id
        self.__done_time = __done_time

    @property
    def is_done(self):
        today = datetime.datetime.utcnow().date()
        return self.__done_time.date() == today

    @is_done.setter
    def is_done(self, is_done: bool) -> bool:
        if is_done:
            self.__done_time = datetime.datetime.utcnow()
        else:
            self.__done_time = datetime.datetime.fromtimestamp(0)

    @property
    def done_date(self) -> datetime.date:
        return self.__done_time.date()

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)
