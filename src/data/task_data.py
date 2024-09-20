"""
タスクデータの構造と操作

役割:
- タスクデータの定義と管理

主な機能:
- タスクオブジェクトの定義（ID、タイトル、説明、状態、親タスクIDなど）
- タスクデータのシリアライズ/デシリアライズ

使用するクラス/モジュール:
- dataclasses (Pythonの標準ライブラリ)

注意点:
- タスクの階層構造を効率的に表現できるデータ構造を選択すること
- タスクの状態変更履歴を追跡できるようにすること
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from enum import Enum

class TaskPriority(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    status: str = "未着手"
    parent_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    subtasks: List['Task'] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.LOW  # デフォルトを低に設定
    due_date: Optional[datetime] = None

    def to_dict(self):
        task_dict = asdict(self)
        task_dict['priority'] = self.priority.value
        task_dict['subtasks'] = [subtask.to_dict() for subtask in self.subtasks]
        return task_dict

    @classmethod
    def from_dict(cls, data):
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])
        subtasks = data.pop('subtasks', [])
        task = cls(**data)
        task.subtasks = [cls.from_dict(subtask) for subtask in subtasks]
        return task

class TaskManager:
    def __init__(self, database):
        self.database = database

    def create_task(self, task: Task) -> int:
        query = '''
            INSERT INTO tasks (title, description, status, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (task.title, task.description, task.status, task.parent_id,
                  task.created_at, task.updated_at)
        task_id = self.database.execute_insert(query, params)
        self._add_task_history(task_id, task.status)
        return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        query = "SELECT * FROM tasks WHERE id = ?"
        result = self.database.execute_query(query, (task_id,))
        if result:
            return Task.from_dict(result[0])
        return None

    def update_task(self, task: Task) -> bool:
        old_task = self.get_task(task.id)
        query = '''
            UPDATE tasks
            SET title = ?, description = ?, status = ?, parent_id = ?, updated_at = ?
            WHERE id = ?
        '''
        params = (task.title, task.description, task.status, task.parent_id,
                  datetime.now(), task.id)
        updated = self.database.execute_update(query, params) > 0
        if updated and old_task and old_task.status != task.status:
            self._add_task_history(task.id, task.status)
        return updated

    def delete_task(self, task_id: int) -> bool:
        query = "DELETE FROM tasks WHERE id = ?"
        return self.database.execute_update(query, (task_id,)) > 0

    def get_all_tasks(self) -> List[Task]:
        query = "SELECT * FROM tasks"
        results = self.database.execute_query(query)
        return [Task.from_dict(result) for result in results]

    def _add_task_history(self, task_id: int, status: str):
        query = '''
            INSERT INTO task_history (task_id, status)
            VALUES (?, ?)
        '''
        self.database.execute_insert(query, (task_id, status))

    def get_task_history(self, task_id: int) -> List[Dict[str, Any]]:
        query = '''
            SELECT * FROM task_history
            WHERE task_id = ?
            ORDER BY changed_at DESC
        '''
        return self.database.execute_query(query, (task_id,))