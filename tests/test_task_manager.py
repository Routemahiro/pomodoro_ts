import unittest
from datetime import datetime, timedelta
from src.core.task_manager import TaskManager
from src.data.database import Database
from src.utils.config import config

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.config = config
        self.database = Database(self.config)
        self.task_manager = TaskManager(self.database)

    def test_create_task(self):
        task_id = self.task_manager.create_task("テストタスク", "説明", priority=1, due_date=datetime.now() + timedelta(days=1))
        self.assertIsNotNone(task_id)

    def test_get_tasks_by_priority(self):
        self.task_manager.create_task("低優先度タスク", priority=0)
        self.task_manager.create_task("高優先度タスク", priority=2)
        tasks = self.task_manager.get_tasks_by_priority()
        self.assertEqual(tasks[0].priority, 2)
        self.assertEqual(tasks[-1].priority, 0)

    def test_get_tasks_by_due_date(self):
        self.task_manager.create_task("明日のタスク", due_date=datetime.now() + timedelta(days=1))
        self.task_manager.create_task("今日のタスク", due_date=datetime.now())
        tasks = self.task_manager.get_tasks_by_due_date()
        self.assertEqual(tasks[0].title, "今日のタスク")
        self.assertEqual(tasks[-1].title, "明日のタスク")

if __name__ == '__main__':
    unittest.main()