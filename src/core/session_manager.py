"""
セッション管理

役割:
- 現在のセッション状態の管理
- セッション履歴の記録

主な機能:
- セッションの開始、終了、一時停止
- セッション統計の計算（総作業時間、完了したポモドーロ数など）

使用するクラス/モジュール:
- data.database.Database
- utils.config.Config

注意点:
- セッションデータの整合性を保つこと（途中で異常終了した場合の処理など）
- 長期間の使用でもパフォーマンスが低下しないよう、適切なデータ管理を行うこと
"""

from datetime import datetime, timedelta
from src.data.database import Database
from src.utils.config import config

class SessionManager:
    def __init__(self, database: Database, config):
        self.database = database
        self.config = config
        self.current_session = None

    def start_session(self, task_id: int = None):
        if self.current_session:
            self.end_session()
        
        self.current_session = {
            'start_time': datetime.now(),
            'task_id': task_id
        }

    def end_session(self):
        if self.current_session:
            end_time = datetime.now()
            duration = (end_time - self.current_session['start_time']).total_seconds()
            
            query = '''
                INSERT INTO sessions (start_time, end_time, duration, task_id)
                VALUES (?, ?, ?, ?)
            '''
            params = (
                self.current_session['start_time'],
                end_time,
                duration,
                self.current_session['task_id']
            )
            self.database.execute_insert(query, params)
            
            self.current_session = None

    def pause_session(self):
        if self.current_session:
            self.end_session()

    def resume_session(self, task_id: int = None):
        self.start_session(task_id)

    def get_session_statistics(self, start_date: datetime, end_date: datetime):
        query = '''
            SELECT COUNT(*) as session_count, SUM(duration) as total_duration
            FROM sessions
            WHERE start_time BETWEEN ? AND ?
        '''
        params = (start_date, end_date)
        result = self.database.execute_query(query, params)[0]
        
        return {
            'session_count': result['session_count'],
            'total_duration': result['total_duration'],
            'completed_pomodoros': result['session_count'] // 2  # 作業セッションと休憩セッションで1ポモドーロ
        }

    def get_recent_sessions(self, limit: int = 10):
        query = '''
            SELECT * FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        '''
        return self.database.execute_query(query, (limit,))

    def clear_old_sessions(self, months: int = 3):
        cutoff_date = datetime.now() - timedelta(days=30*months)
        query = '''
            DELETE FROM sessions
            WHERE start_time < ?
        '''
        deleted_count = self.database.execute_update(query, (cutoff_date,))
        print(f"{deleted_count}件の古いセッションデータを削除しました。")

    def get_today_stats(self):
        # ここに今日の統計情報を取得するロジックを実装する
        # 仮の実装として、ダミーデータを返す
        return {
            "completed_pomodoros": 0,
            "total_focus_time": 0,
            "completed_tasks": 0
        }