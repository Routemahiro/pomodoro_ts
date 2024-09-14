"""
データベース操作

役割:
- SQLiteデータベースの初期化と操作

主な機能:
- テーブルの作成と管理
- データの挿入、更新、削除、取得

使用するクラス/モジュール:
- sqlite3
- utils.config.Config

注意点:
- SQLインジェクション攻撃を防ぐため、パラメータ化クエリを使用すること
- 大量のデータを扱う場合はインデックスの適切な設定を行うこと
- トランザクション処理を適切に行い、データの一貫性を保つこと
"""

import sqlite3
import threading
from src.utils.config import config
from typing import List, Dict, Any
import logging

class Database:
    def __init__(self, config):
        self.db_path = config.get('database_path', 'data/pomodoro.db')
        self.lock = threading.Lock()  # ロックを追加
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)  # check_same_thread=False を設定
        self.conn.row_factory = sqlite3.Row
        self.initialize_database()

    def initialize_database(self):
        with self.lock:  # ロックを使用
            cursor = self.conn.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    parent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES tasks (id)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration REAL NOT NULL,
                    task_id INTEGER,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                );

                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY,
                    message TEXT,
                    role TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER,
                    status TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                );
            ''')
            # 他のテーブル初期化も同様にロック内で行う
            self.conn.commit()

    def create_indexes(self):
        with self.lock:  # ロックを使用
            self.conn.executescript('''
                CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks (parent_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_task_id ON sessions (task_id);
                CREATE INDEX IF NOT EXISTS idx_ai_conversations_timestamp ON ai_conversations (timestamp);
                CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history (task_id);
            ''')

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.lock:  # ロックを使用
            try:
                cursor = self.conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except sqlite3.Error as e:
                logging.error(f"データベースクエリの実行中にエラーが発生しました: {e}")
                raise

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        with self.lock:  # ロックを使用
            try:
                cursor = self.conn.execute(query, params)
                self.conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                logging.error(f"データの挿入中にエラーが発生しました: {e}")
                raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        with self.lock:  # ロックを使用
            try:
                cursor = self.conn.execute(query, params)
                self.conn.commit()
                return cursor.rowcount
            except sqlite3.Error as e:
                logging.error(f"データの更新中にエラーが発生しました: {e}")
                raise

    def close(self):
        with self.lock:  # ロックを使用
            if self.conn:
                self.conn.close()