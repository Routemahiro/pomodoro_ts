"""
ダッシュボードウィジェット

役割:
- 現在の作業状況の表示
- 今日の達成タスク数の表示

主な機能:
- 折りたたみ可能なウィジェット
- リアルタイムでの情報更新

使用するクラス/モジュール:
- core.session_manager.SessionManager
- core.task_manager.TaskManager
- utils.ui_helpers

注意点:
- 情報の更新はイベントドリブンで行い、不要な再描画を避けること
"""