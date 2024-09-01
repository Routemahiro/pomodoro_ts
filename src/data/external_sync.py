"""
このファイルは、外部サービスとの連携を担当します。
主な役割:
- QObjectを継承した外部同期クラスの実装
- Todoist, Trelloなどの外部サービスとのデータ同期
- タスク情報の取得と更新

連携するファイル:
- data/database.py: 同期データの保存
- gui/dashboard_widget.py: 外部タスク情報の表示（シグナル発信）
- utils/config.py: 外部サービスの認証情報取得
"""