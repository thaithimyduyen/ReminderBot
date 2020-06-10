#!/usr/bin/env python3
import enum


class Level_Habbit(enum.Enum):
    EASY = "0"
    MEDIUM = "1"
    HARD = "2"


class Habbit:
    def __init__(
        self, name
    ):
        self.name = name
        # self.level = Level_Habbit.EASY

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)
