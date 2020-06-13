#!/usr/bin/env python3
import enum
import uuid

MessageId = str
ChatId = str


class LevelHabit(enum.Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class StateHabit(enum.Enum):
    DONE = 1
    NOT_DONE = 0


class Mark(enum.Enum):
    DONE = "✅"
    NOT_DONE = "⬜"
    DELETE = "🗑"


class Habit:
    def __init__(
        self, name
    ):
        self.name = name
        self.state = StateHabit.NOT_DONE
        self.id = str(uuid.uuid1())
        # self.level = LevelHabit.EASY

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)
