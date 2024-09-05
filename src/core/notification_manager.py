"""
通知管理

役割:
- システム通知の送信管理

主な機能:
- タイマー完了時の通知
- 重要なイベント（長時間の作業など）の通知

使用するクラス/モジュール:
- utils.config.Config

注意点:
- OSはWindowsのみ対応
- ユーザー設定に基づいて通知の on/off を切り替えられるようにすること
"""

from src.utils.config import config
from win10toast import ToastNotifier
import threading

class NotificationManager:
    def __init__(self, config):
        self.config = config
        self.toaster = ToastNotifier()

    def send_notification(self, title: str, message: str):
        if self.config.get('notifications_enabled', True):
            threading.Thread(target=self._show_notification, args=(title, message)).start()

    def _show_notification(self, title: str, message: str):
        self.toaster.show_toast(
            title,
            message,
            duration=5,
            threaded=True
        )

    def notify_timer_complete(self, timer_type: str):
        title = "タイマー終了"
        message = f"{timer_type}の時間が終了しました。"
        self.send_notification(title, message)

    def notify_long_work_session(self, duration: int):
        if duration > self.config.get('long_work_session_threshold', 120 * 60):  # デフォルト2時間
            title = "長時間作業の警告"
            message = f"{duration // 60}分間連続で作業しています。休憩を取ることをおすすめします。"
            self.send_notification(title, message)

    def notify_task_completion(self, task_title: str):
        title = "タスク完了"
        message = f"タスク「{task_title}」が完了しました。お疲れ様でした！"
        self.send_notification(title, message)

    def notify_daily_goal_achieved(self):
        title = "日次目標達成"
        message = "今日の目標を達成しました！素晴らしい成果です！"
        self.send_notification(title, message)