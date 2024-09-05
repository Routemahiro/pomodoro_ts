"""
アプリケーション設定の管理

役割:
- ユーザー設定の保存と読み込み

主な機能:
- 設定のシリアライズ/デシリアライズ
- デフォルト設定の提供
- 設定変更の通知

注意点:
- 設定ファイルの破損に備えて、バックアップと復元機能を実装すること
- 機密情報（APIキーなど）は暗号化して保存すること
"""

import json
import os
from typing import Any, Dict
import logging
from cryptography.fernet import Fernet

class SettingsManager:
    def __init__(self):
        self.settings_file = 'data/settings.json'
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)

    def _get_or_create_encryption_key(self):
        key_file = 'data/encryption_key.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data.encode()).decode()
                return json.loads(decrypted_data)
            except Exception as e:
                logging.error(f"設定ファイルの読み込みに失敗しました: {e}")
        return self.get_default_settings()

    def save(self, settings: Dict[str, Any]):
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(settings).encode()).decode()
            with open(self.settings_file, 'w') as f:
                f.write(encrypted_data)
        except Exception as e:
            logging.error(f"設定ファイルの保存に失敗しました: {e}")

    def get_default_settings(self) -> Dict[str, Any]:
        return {
            'work_time': 25 * 60,
            'short_break': 5 * 60,
            'long_break': 15 * 60,
            'pomodoros_before_long_break': 4,
            'color_primary': "#4CAF50",
            'color_secondary': "#2196F3",
            'color_accent': "#FFC107",
            'color_background': "#FFFFFF",
            'color_text': "#333333",
        }

    def create_backup(self):
        backup_file = f"{self.settings_file}.bak"
        try:
            with open(self.settings_file, 'r') as source, open(backup_file, 'w') as target:
                target.write(source.read())
            logging.info("設定ファイルのバックアップを作成しました。")
        except Exception as e:
            logging.error(f"バックアップの作成に失敗しました: {e}")

    def restore_from_backup(self):
        backup_file = f"{self.settings_file}.bak"
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as source, open(self.settings_file, 'w') as target:
                    target.write(source.read())
                logging.info("設定ファイルをバックアップから復元しました。")
            except Exception as e:
                logging.error(f"バックアップの復元に失敗しました: {e}")
        else:
            logging.warning("バックアップファイルが見つかりません。")