#!/usr/bin/env python3

import redis

from typing import List
from app.entities import Task, UserId


class TaskRepository:
    def __init__(self, kv: redis.Redis):
        self._kv = kv

    @staticmethod
    def _key(user_id: UserId, suffix: str = "") -> str:
        return "reminder_bot:" + str(user_id) + suffix

    def add(self, task: Task, user_id: UserId) -> None:
        self._kv.hmset(self._key(user_id), {
            task.name: task.to_json(),
        })

    def get_all(self, user_id: UserId) -> List[Task]:
        key = self._key(user_id)
        tasks = self._kv.hvals(key)
        return list(map(Task.from_json, tasks))

    def delete(self, user_id: UserId, task: Task) -> None:
        key = self._key(user_id)
        self._kv.hdel(key, task.name)

    def get_last_start(self, user_id: UserId) -> str:
        key = self._key(user_id, ":last_start")
        value = self._kv.get(key)
        return "" if value is None else value

    def set_last_start(self, user_id: UserId, current_time: str) -> None:
        key = self._key(user_id, ":last_start")
        self._kv.set(key, current_time)
