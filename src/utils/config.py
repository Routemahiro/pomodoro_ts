"""
設定管理

役割:
- アプリケーション全体の設定を一元管理

主な機能:
- 設定値の取得と設定
- 設定変更の通知（Observer パターンの実装）

使用するクラス/モジュール:
- data.settings_manager.SettingsManager

注意点:
- スレッドセーフな実装を心がけること
- 設定変更時は関連するモジュールに適切に通知すること
"""