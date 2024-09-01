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