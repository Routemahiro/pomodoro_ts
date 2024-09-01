"""
タスクデータの構造と操作

役割:
- タスクデータの定義と管理

主な機能:
- タスクオブジェクトの定義（ID、タイトル、説明、状態、親タスクIDなど）
- タスクデータのシリアライズ/デシリアライズ

使用するクラス/モジュール:
- dataclasses (Pythonの標準ライブラリ)

注意点:
- タスクの階層構造を効率的に表現できるデータ構造を選択すること
- タスクの状態変更履歴を追跡できるようにすること
"""