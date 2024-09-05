"""
タスク管理のコアロジック

役割:
- タスクの追加、編集、削除、状態管理

主な機能:
- タスクのCRUD操作
- タスクの階層構造（メインタスク、サブタスク）の管理
- タスクの状態遷移（未開始→進行中→完了）

使用するクラス/モジュール:
- data.database.Database
- data.task_data.TaskData

注意点:
- タスクデータの一貫性を保つこと（親タスクと子タスクの関係など）
- 大量のタスクがある場合のパフォーマンスに注意
"""

from src.data.database import Database
from src.data.task_data import Task, TaskManager as DataTaskManager
from datetime import datetime
from typing import List

class TaskManager:
    def __init__(self, database: Database, config):  # configパラメータを追加
        self.database = database
        self.config = config  # configを保存
        self.data_task_manager = DataTaskManager(database)

    def create_task(self, title: str, description: str = "", parent_id: int = None, priority: int = 0, due_date: datetime = None) -> int:
        task = Task(title=title, description=description, parent_id=parent_id, priority=priority, due_date=due_date)
        return self.data_task_manager.create_task(task)

    def get_task(self, task_id: int) -> Task:
        return self.data_task_manager.get_task(task_id)

    def update_task(self, task: Task) -> bool:
        return self.data_task_manager.update_task(task)

    def delete_task(self, task_id: int) -> bool:
        return self.data_task_manager.delete_task(task_id)

    def get_all_tasks(self):
        return self.data_task_manager.get_all_tasks()

    def get_task_tree(self):
        all_tasks = self.get_all_tasks()
        task_dict = {task.id: task for task in all_tasks}
        
        root_tasks = []
        for task in all_tasks:
            if task.parent_id is None:
                root_tasks.append(task)
            else:
                parent = task_dict.get(task.parent_id)
                if parent:
                    parent.subtasks.append(task)
        
        return root_tasks

    def change_task_status(self, task_id: int, new_status: str) -> bool:
        task = self.get_task(task_id)
        if task:
            task.status = new_status
            return self.update_task(task)
        return False

    def move_task(self, task_id: int, new_parent_id: int = None) -> bool:
        task = self.get_task(task_id)
        if task:
            task.parent_id = new_parent_id
            return self.update_task(task)
        return False

    def get_task_history(self, task_id: int):
        return self.data_task_manager.get_task_history(task_id)

    def get_tasks_by_priority(self) -> List[Task]:
        return sorted(self.get_all_tasks(), key=lambda t: t.priority, reverse=True)

    def get_tasks_by_due_date(self) -> List[Task]:
        return sorted(self.get_all_tasks(), key=lambda t: t.due_date or datetime.max)

    def get_completed_tasks_count(self) -> int:
        completed_tasks = [task for task in self.get_all_tasks() if task.status == 'completed']
        return len(completed_tasks)