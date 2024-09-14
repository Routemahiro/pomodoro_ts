"""
設定ダイアログ

役割:
- ユーザー設定の変更インターフェース

主な機能:
- 作業時間、休憩時間の設定
- 通知設定
- テーマ設定
- APIキーの設定

使用するクラス/モジュール:
- utils.config.Config
- utils.ui_helpers

注意点:
- 設定変更後は即座に反映し、Configオブジェクトを更新すること
- APIキーなどの機密情報は適切に暗号化して保存すること
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QCheckBox, QComboBox, QLineEdit, QPushButton
from src.utils.config import config
from src.utils.ui_helpers import create_button

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.config.load()  # 設定を読み込む
        self.setWindowTitle("設定")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 作業時間設定
        self.work_time_spinbox = QSpinBox()
        self.work_time_spinbox.setRange(1, 120)
        self.work_time_spinbox.setValue(self.config.get('work_time', 25 * 60) // 60)  # 秒を分に変換
        form_layout.addRow("作業時間 (分):", self.work_time_spinbox)

        # 短い休憩時間設定
        self.short_break_spinbox = QSpinBox()
        self.short_break_spinbox.setRange(1, 30)
        self.short_break_spinbox.setValue(self.config.get('short_break', 5 * 60) // 60)  # 秒を分に変換
        form_layout.addRow("短い休憩時間 (分):", self.short_break_spinbox)

        # 長い休憩時間設定
        self.long_break_spinbox = QSpinBox()
        self.long_break_spinbox.setRange(1, 60)
        self.long_break_spinbox.setValue(self.config.get('long_break', 15 * 60) // 60)  # 秒を分に変換
        form_layout.addRow("長い休憩時間 (分):", self.long_break_spinbox)

        # 通知設定
        self.notification_checkbox = QCheckBox()
        self.notification_checkbox.setChecked(self.config.get('notifications_enabled', True))
        form_layout.addRow("通知を有効にする:", self.notification_checkbox)

        # テーマ設定
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(["ライト", "ダーク"])
        self.theme_combobox.setCurrentText(self.config.get('theme', "ライト"))
        form_layout.addRow("テーマ:", self.theme_combobox)

        # APIキー設定
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config.get('openai_api_key', ''))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("OpenAI APIキー:", self.api_key_input)

        # テストモード設定
        self.test_mode_checkbox = QCheckBox("テストモード")
        self.test_mode_checkbox.setChecked(self.config.get('test_mode', False))
        form_layout.addRow("テストモード:", self.test_mode_checkbox)

        # 手動セッション切り替え設定を追加
        self.manual_switch_checkbox = QCheckBox("手動セッション切り替え")
        self.manual_switch_checkbox.setChecked(self.config.get('manual_session_switch', False))
        form_layout.addRow("手動セッション切り替え:", self.manual_switch_checkbox)

        layout.addLayout(form_layout)

        # 保存ボタン
        save_button = create_button("保存", style_class="primary")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self):
        old_theme = self.config.get('theme', 'ライト')
        new_theme = self.theme_combobox.currentText()

        self.config.set('work_time', self.work_time_spinbox.value() * 60)
        self.config.set('short_break', self.short_break_spinbox.value() * 60)
        self.config.set('long_break', self.long_break_spinbox.value() * 60)
        self.config.set('notifications_enabled', self.notification_checkbox.isChecked())
        self.config.set('theme', new_theme)
        self.config.set('openai_api_key', self.api_key_input.text())
        self.config.set('test_mode', self.test_mode_checkbox.isChecked())
        # 手動セッション切り替え設定の保存
        self.config.set('manual_session_switch', self.manual_switch_checkbox.isChecked())
        self.config.save()

        # テーマが変更された場合、メインウィンドウのテーマを更新
        if old_theme != new_theme:
            self.parent().apply_theme()

        self.accept()