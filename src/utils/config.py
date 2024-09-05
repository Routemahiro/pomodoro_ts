"""
設定管理

役割:
- アプリケーション全体の設定を一元管理

主な機能:
- 設定値の取得と設定
- 設定変更の通知（Observer パターンの実装）

注意点:
- スレッドセーフな実装を心がけること
- 設定変更時は関連するモジュールに適切に通知すること
"""
from typing import Any, Callable
import threading

class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._settings = {}
        self._observers = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        self._settings[key] = value
        self._notify_observers(key, value)

    def register_observer(self, key: str, callback: Callable[[str, Any], None]):
        if key not in self._observers:
            self._observers[key] = set()
        self._observers[key].add(callback)

    def unregister_observer(self, key: str, callback: Callable[[str, Any], None]):
        if key in self._observers:
            self._observers[key].discard(callback)

    def _notify_observers(self, key: str, value: Any):
        if key in self._observers:
            for callback in self._observers[key]:
                callback(key, value)

    def load(self):
        """設定をファイルから読み込む"""
        from src.data.settings_manager import SettingsManager
        settings_manager = SettingsManager()
        self._settings = settings_manager.load()

    def save(self):
        """現在の設定をファイルに保存する"""
        from src.data.settings_manager import SettingsManager
        settings_manager = SettingsManager()
        settings_manager.save(self._settings)

config = Config()