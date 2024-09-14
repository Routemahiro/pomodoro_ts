"""
アプリケーションのメインウィンドウGUI

役割:
- メインウィンドウのレイアウト設定
- 各ウィジェットの配置と管理
- キーボードショートカットの設定

主なコンポーネント:
- TimerWidget: 左上に配置
- CharacterWidget: 中央に大きく配置
- DashboardWidget: 左下に配置（折りたたみ可能）
- SlidePanel: 右側にスライドインするパネル（TaskPanel, AIChatPanel）
- ボタン群: 右下に配置（Start Timer, Reset Timer, Tasks, AI Chat, Settings）

使用するクラス/モジュール:
- gui.timer_widget.TimerWidget
- gui.character_widget.CharacterWidget
- gui.dashboard_widget.DashboardWidget
- gui.slide_panel.SlidePanel
- gui.task_panel.TaskPanel
- gui.ai_chat_panel.AIChatPanel
- gui.settings_dialog.SettingsDialog
- gui.report_window.ReportWindow
- utils.ui_helpers

注意点:
- レスポンシブデザインを心がけ、ウィンドウサイズの変更に対応すること
- キャラクターウィジェットが他の要素と重ならないよう、適切なz-indexを設定すること
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QSize
from src.gui.timer_widget import TimerWidget
from src.gui.character_widget import CharacterWidget
from src.gui.dashboard_widget import DashboardWidget
from src.gui.slide_panel import SlidePanel
from src.gui.task_panel import TaskPanel
from src.gui.ai_chat_panel import AIChatPanel
from src.gui.settings_dialog import SettingsDialog
from src.gui.report_window import ReportWindow
from src.utils.ui_helpers import create_button, load_stylesheet
from src.core.timer import TimerState, TimerType  # この行を修正

class MainWindow(QMainWindow):
    def __init__(self, timer, session_manager, task_manager, ai_interface, config):
        super().__init__()
        self.timer = timer
        self.session_manager = session_manager
        self.task_manager = task_manager
        self.ai_interface = ai_interface
        self.config = config

        self.central_widget = QWidget()
        self.central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("Pomodoro AI Assistant")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()
        self.setup_shortcuts()
        self.setup_config_observers()
        self.apply_theme()  # テーマを適用

    # apply_stylesheetメソッドを削除

    def apply_theme(self):
        theme = self.config.get('theme', 'ライト')
        self.update_theme('theme', theme)

    def update_theme(self, key, value):
        try:
            if value == "ダーク":
                stylesheet = load_stylesheet("resources/styles/dark_style.qss")
            else:
                stylesheet = load_stylesheet("resources/styles/style.qss")
            
            if stylesheet:
                self.setStyleSheet(stylesheet)
                # 子ウィジェットにもスタイルシートを適用
                for child in self.findChildren(QWidget):
                    child.setStyleSheet(stylesheet)
            else:
                print(f"警告: {value}モードのスタイルシートが空です。")
        except FileNotFoundError:
            print(f"警告: {value}モードのスタイルシートファイルが見つかりません。")
        except Exception as e:
            print(f"スタイルシートの読み込み中にエラーが発生しました: {e}")

    def show_settings_dialog(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # 設定が変更された場合、必要に応じて追加の処理を行う
            pass

    def show_report_window(self):
        report_window = ReportWindow(self.session_manager, self.task_manager, self)
        report_window.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # キャラクターウィジェットのサイズ調整
        available_height = self.height() - self.timer_widget.height() - 20  # 20はマージン
        character_height = min(600, available_height)
        self.character_widget.setFixedSize(QSize(400, character_height))

    def setup_config_observers(self):
        self.config.register_observer('work_time', self.update_timer_settings)
        self.config.register_observer('short_break', self.update_timer_settings)
        self.config.register_observer('long_break', self.update_timer_settings)
        self.config.register_observer('theme', self.update_theme)
        # 他の設定項目も必要に応じて追加

    def update_timer_settings(self, key, value):
        self.timer.update_settings(self.config)

    def setup_ui(self):
        # 左側のレイアウト
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # タイマーと円形進捗バー
        timer_layout = QVBoxLayout()
        timer_layout.setContentsMargins(0, 0, 0, 0)
        self.timer_widget = TimerWidget(self.timer)
        timer_layout.addWidget(self.timer_widget, alignment=Qt.AlignCenter)
        
        # Startとリセットボタン
        timer_buttons = QHBoxLayout()
        self.start_pause_button = create_button("Start", style_class="primary")
        self.reset_button = create_button("Reset", style_class="secondary")
        self.reset_button.setEnabled(False)  # 初期状態では無効化
        self.reset_button.setProperty("disabled", True)  # この行を追加
        timer_buttons.addWidget(self.start_pause_button)
        timer_buttons.addWidget(self.reset_button)

        # 次のセッションへボタンを追加
        self.next_session_button = create_button("次のセッションへ", style_class="secondary")
        self.next_session_button.setVisible(False)  # 初期は非表示
        timer_buttons.addWidget(self.next_session_button)

        timer_layout.addLayout(timer_buttons)

        left_layout.addLayout(timer_layout)

        # キャラクター表示エリア
        self.character_widget = CharacterWidget(self.config)
        self.character_widget.setFixedSize(QSize(400, 600))
        left_layout.addWidget(self.character_widget, alignment=Qt.AlignCenter)

        left_layout.addStretch(1)

        # 右側のレイアウト
        right_layout = QVBoxLayout()

        # TasksとAI Chatボタン
        top_buttons = QHBoxLayout()
        self.tasks_button = create_button("Tasks", style_class="secondary")
        self.ai_chat_button = create_button("AI Chat", style_class="secondary")
        top_buttons.addWidget(self.tasks_button)
        top_buttons.addWidget(self.ai_chat_button)
        right_layout.addLayout(top_buttons)

        # ダッシュボード
        self.dashboard_widget = DashboardWidget(self.session_manager, self.task_manager)
        right_layout.addWidget(self.dashboard_widget)

        right_layout.addStretch(1)

        # 設定ボタン
        self.settings_button = create_button("Settings", style_class="secondary")
        right_layout.addWidget(self.settings_button, alignment=Qt.AlignRight | Qt.AlignBottom)

        # メインレイアウトに追加
        self.main_layout.addLayout(left_layout, 2)
        self.main_layout.addLayout(right_layout, 1)

        # スライドパネル
        self.slide_panel = SlidePanel(self)
        self.task_panel = TaskPanel(self.task_manager)
        self.ai_chat_panel = AIChatPanel(self.ai_interface, self.task_manager)  # task_managerを追加
        self.slide_panel.add_panel("Tasks", self.task_panel)
        self.slide_panel.add_panel("AI Chat", self.ai_chat_panel)

        self.connect_signals()

    def connect_signals(self):
        # 既存のシグナル接続
        self.start_pause_button.clicked.connect(self.toggle_timer)
        self.reset_button.clicked.connect(self.reset_timer)
        self.timer_widget.timer_updated.connect(self.update_ui_on_timer_update)
        self.timer_widget.timer_updated.connect(self.on_timer_updated)
        
        # 設定ボタンのシグナル接続を追加
        self.settings_button.clicked.connect(self.show_settings_dialog)
        
        # タスクとAIチャットボタンのシグナル接続も追加しておくといいかも
        self.tasks_button.clicked.connect(lambda: self.slide_panel.toggle_panel("Tasks"))
        self.ai_chat_button.clicked.connect(lambda: self.slide_panel.toggle_panel("AI Chat"))
        
        # 次のセッションへボタンのシグナル接続を追加
        self.next_session_button.clicked.connect(self.start_next_session)

    def on_timer_updated(self, state, timer_type, remaining_time, can_reset):
        if timer_type == "WORK":
            self.setWindowTitle("Pomodoro AI Assistant - 作業中")
        elif timer_type == "SHORT_BREAK":
            self.setWindowTitle("Pomodoro AI Assistant - 短い休憩")
        elif timer_type == "LONG_BREAK":
            self.setWindowTitle("Pomodoro AI Assistant - 長い休憩")

    def toggle_timer(self):
        if self.timer.state == TimerState.RUNNING:
            self.timer.pause()
        elif self.timer.state == TimerState.PAUSED:
            self.timer.resume()
        else:  # IDLE状態
            self.timer.start()
        self.update_ui_on_timer_update(self.timer.state.name, self.timer.timer_type.name, self.timer.remaining_time, self.timer.can_reset)

    def reset_timer(self):
        self.timer.reset()
        self.update_ui_on_timer_update(TimerState.IDLE.name, self.timer.timer_type.name, self.timer.remaining_time, False)

    def update_ui_on_timer_update(self, state, timer_type, remaining_time, can_reset):
        if state == TimerState.PAUSED.name:
            self.start_pause_button.setText("Resume")
            self.reset_button.setEnabled(can_reset)
            self.reset_button.setProperty("disabled", not can_reset)
        elif state == TimerState.RUNNING.name:
            self.start_pause_button.setText("Pause")
            self.reset_button.setEnabled(False)
            self.reset_button.setProperty("disabled", True)
        elif state == TimerState.IDLE.name:
            self.start_pause_button.setText("Start")
            self.reset_button.setEnabled(False)
            self.reset_button.setProperty("disabled", True)
        self.reset_button.style().unpolish(self.reset_button)
        self.reset_button.style().polish(self.reset_button)
        self.timer_widget.update_display()

        # 手動セッション切り替えの場合のボタン表示制御
        if self.config.get('manual_session_switch', False):
            if self.timer.state == TimerState.IDLE and remaining_time == 0:
                self.next_session_button.setVisible(True)
            else:
                self.next_session_button.setVisible(False)
        else:
            self.next_session_button.setVisible(False)

    def update_ui_on_timer_stop(self):
        self.start_pause_button.setText("Start")

    def setup_shortcuts(self):
        # キーボードショートカットの設定
        pass

    def start_next_session(self):
        self.timer.start_next_session()
        self.update_ui_on_timer_update(self.timer.state.name, self.timer.timer_type.name, self.timer.remaining_time, self.timer.can_reset)
        self.next_session_button.setVisible(False)  # ボタンを非表示