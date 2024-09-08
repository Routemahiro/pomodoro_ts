"""
タイマーのコアロジック

役割:
- ポモドーロタイマーの実装
- 作業時間、短休憩、長休憩の管理

主な機能:
- タイマーの開始、停止、リセット
- 時間経過の追跡
- セッション（作業→休憩）の自動切り替え

使用するクラス/モジュール:
- utils.config.Config
- core.notification_manager.NotificationManager

注意点:
- マルチスレッド環境での正確な時間管理に注意
- タイマー状態の変更時には適切にシグナルを発行し、GUI更新を促すこと
"""

import time
import threading
from enum import Enum
from src.utils.config import config
from src.core.notification_manager import NotificationManager

class TimerState(Enum):
    IDLE = 0
    RUNNING = 1
    PAUSED = 2

class TimerType(Enum):
    WORK = 0
    SHORT_BREAK = 1
    LONG_BREAK = 2

class Timer:
    def __init__(self, config, notification_manager: NotificationManager):
        self.config = config
        self.notification_manager = notification_manager
        self.state = TimerState.IDLE
        self.timer_type = TimerType.WORK
        self.remaining_time = self.config.get('work_time', 25 * 60)
        self.pomodoro_count = 0
        self.timer_thread = None
        self.observers = []

    def start(self):
        if self.state != TimerState.RUNNING:
            self.state = TimerState.RUNNING
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.start()
            self._notify_observers()

    def pause(self):
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._notify_observers()

    def resume(self):
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._notify_observers()

    def stop(self):
        if self.state != TimerState.IDLE:
            self.state = TimerState.IDLE
            self.remaining_time = self.config.get('work_time', 25 * 60)
            self._notify_observers()

    def _run_timer(self):
        while self.state == TimerState.RUNNING and self.remaining_time > 0:
            time.sleep(1)
            self.remaining_time -= 1
            self._notify_observers()

        if self.remaining_time == 0:
            self._timer_completed()

    def _timer_completed(self):
        self.notification_manager.send_notification("タイマー終了", f"{self.timer_type.name}の時間が終了しました。")
        if self.timer_type == TimerType.WORK:
            self.pomodoro_count += 1
            if self.pomodoro_count % self.config.get('pomodoros_before_long_break', 4) == 0:
                self._switch_to_long_break()
            else:
                self._switch_to_short_break()
        else:
            self._switch_to_work()

    def _switch_to_work(self):
        self.timer_type = TimerType.WORK
        self.remaining_time = self.config.get('work_time', 25 * 60)
        self._notify_observers()

    def _switch_to_short_break(self):
        self.timer_type = TimerType.SHORT_BREAK
        self.remaining_time = self.config.get('short_break', 5 * 60)
        self._notify_observers()

    def _switch_to_long_break(self):
        self.timer_type = TimerType.LONG_BREAK
        self.remaining_time = self.config.get('long_break', 15 * 60)
        self._notify_observers()

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def _notify_observers(self):
        for observer in self.observers:
            observer(self.state, self.timer_type, self.remaining_time)

    def update_settings(self, config):
        self.work_time = config.get('work_time')
        self.short_break = config.get('short_break')
        self.long_break = config.get('long_break')
        # タイマーの表示を更新する処理を追加