"""
アプリケーション使用状況追跡

役割:
- アクティブウィンドウの監視
- アプリケーション使用時間の記録

主な機能:
- 現在のアクティブウィンドウの取得（OS APIを使用）
- アプリケーションごとの使用時間の集計

使用するクラス/モジュール:
- data.database.Database
- utils.config.Config

注意点:
- OSはWindowsのみ対応
- プライバシーに配慮し、必要最小限の情報のみを記録すること
"""

import win32gui
import win32process
import psutil
import time
from src.data.database import Database
from src.utils.config import config
import threading

class ActivityTracker:
    def __init__(self, database: Database, config):
        self.database = database
        self.config = config
        self.is_tracking = False
        self.tracking_thread = None
        self.current_app = ""
        self.start_time = 0

    def start_tracking(self):
        if not self.is_tracking:
            self.is_tracking = True
            self.tracking_thread = threading.Thread(target=self._track_activity)
            self.tracking_thread.start()

    def stop_tracking(self):
        self.is_tracking = False
        if self.tracking_thread:
            self.tracking_thread.join()

    def _track_activity(self):
        while self.is_tracking:
            new_app = self._get_active_window_title()
            current_time = time.time()

            if new_app != self.current_app:
                if self.current_app:
                    duration = current_time - self.start_time
                    self._save_activity(self.current_app, duration)

                self.current_app = new_app
                self.start_time = current_time

            time.sleep(1)  # 1秒ごとにチェック

    def _get_active_window_title(self):
        try:
            window = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(window)
            app_name = psutil.Process(pid).name()
            return app_name
        except:
            return "Unknown"

    def _save_activity(self, app_name: str, duration: float):
        query = '''
            INSERT INTO app_usage (app_name, duration, timestamp)
            VALUES (?, ?, ?)
        '''
        self.database.execute_insert(query, (app_name, duration, time.time()))

    def get_daily_usage_stats(self):
        query = '''
            SELECT app_name, SUM(duration) as total_duration
            FROM app_usage
            WHERE timestamp > ?
            GROUP BY app_name
            ORDER BY total_duration DESC
        '''
        today_start = time.time() - 86400  # 24時間前
        return self.database.execute_query(query, (today_start,))

    def get_productivity_score(self):
        productive_apps = self.config.get('productive_apps', [])
        daily_stats = self.get_daily_usage_stats()
        
        total_time = sum(stat['total_duration'] for stat in daily_stats)
        productive_time = sum(stat['total_duration'] for stat in daily_stats if stat['app_name'] in productive_apps)
        
        if total_time > 0:
            return (productive_time / total_time) * 100
        return 0