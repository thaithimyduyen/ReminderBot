#!/usr/bin/env python3

import redis

from typing import List
from app.entities import Task, UserId


class TaskRepository:
    def __init__(self, kv: redis.Redis):
        self._kv = kv

    @staticmethod
    def _prefix_key(user_id: UserId) -> str:
        return "Reminder Bot:" + str(user_id)

    def add(self, task: Task, user_id: UserId) -> None:
        self._kv.hmset(self._prefix_key(user_id), {
            task.name: task.to_json(),
        })

    def get_all(self, user_id: UserId) -> List[Task]:
        key = self._prefix_key(user_id)
        tasks = self._kv.hvals(key)
        return list(map(Task.from_json, tasks))

    def delete(self, user_id: UserId, task: Task) -> None:
        key = self._prefix_key(user_id)
        self._kv.hdel(key, task.name)
