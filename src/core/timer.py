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
        self.paused = False
        self.start_time = 0
        self.last_update_time = 0  # 新しく追加
        self.can_reset = False  # リセットボタンの状態を管理する新しい変数

    def start(self):
        if self.state != TimerState.RUNNING:
            self.state = TimerState.RUNNING
            self.start_time = time.time()
            self.last_update_time = self.start_time  # 初期化
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.start()
            self._notify_observers()

    def pause(self):
        if self.state == TimerState.RUNNING and not self.paused:
            current_time = time.time()
            elapsed_time = current_time - self.last_update_time
            self.remaining_time -= elapsed_time  # 残り時間を正確に計算
            self.paused = True
            self.paused_time = current_time - self.start_time
            self.state = TimerState.PAUSED
            self.can_reset = True  # 一時停止状態でリセット可能に
            self._notify_observers()

    def resume(self):
        if self.state == TimerState.PAUSED:
            self.paused = False
            self.start_time = time.time() - self.paused_time
            self.last_update_time = time.time()  # 更新
            self.state = TimerState.RUNNING
            self.can_reset = False  # 再開時にリセット不可に
            self._notify_observers()

    def stop(self):
        if self.state != TimerState.IDLE and self.can_reset:
            self.state = TimerState.IDLE
            self.timer_type = TimerType.WORK  # 常に作業セッションに戻る
            self.remaining_time = self.config.get('work_time', 25 * 60)
            self.can_reset = False
            self._notify_observers()

    def _run_timer(self):
        while self.state in [TimerState.RUNNING, TimerState.PAUSED] and self.remaining_time > 0:
            if not self.paused:
                current_time = time.time()
                elapsed_time = current_time - self.last_update_time
                self.remaining_time -= elapsed_time
                self.last_update_time = current_time
                self._notify_observers()
            time.sleep(0.1)  # より短い間隔でチェック

        if self.remaining_time <= 0:
            self.remaining_time = 0
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
            observer(self.state, self.timer_type, self.remaining_time, self.can_reset)

    def update_settings(self, config):
        self.work_time = config.get('work_time')
        self.short_break = config.get('short_break')
        self.long_break = config.get('long_break')
        # タイマーの表示を更新する処理を追加

    def is_running(self):
        return self.state == TimerState.RUNNING and not self.paused