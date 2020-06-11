#!/usr/bin/env python3
import enum

MessageId = str
ChatId = str


class LevelHabit(enum.Enum):
    EASY = "0"
    MEDIUM = "1"
    HARD = "2"


class StateHabit(enum.Enum):
    DONE = "1"
    NOT_DONE = "0"


class Mark(enum.Enum):
    DONE = "✅"
    NOT_DONE = "⬜"


class Habit:
    def __init__(
        self, name
    ):
        self.name = name
        self.state = StateHabit.NOT_DONE
        # self.level = LevelHabit.EASY

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)
