"""
ヘルパー関数

役割:
- アプリケーション全体で使用する汎用的な関数を提供

主な機能:
- 時間フォーマットの変換
- データ処理ユーティリティ
- 文字列操作ユーティリティ

注意点:
- パフォーマンスを考慮した実装を心がけること
- 可能な限り、副作用のない純粋関数として実装すること
"""
from datetime import timedelta
import re
import uuid

def format_time(seconds: int) -> str:
    """秒数を「MM:SS」形式の文字列に変換する"""
    return str(timedelta(seconds=seconds))[2:7]

def parse_time(time_str: str) -> int:
    """「MM:SS」形式の文字列を秒数に変換する"""
    match = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    raise ValueError("Invalid time format. Use 'MM:SS'.")

def truncate_string(text: str, max_length: int) -> str:
    """文字列を指定された長さに切り詰める"""
    return text[:max_length] + '...' if len(text) > max_length else text

def generate_unique_id() -> str:
    """一意のIDを生成する"""
    return str(uuid.uuid4())

def sanitize_input(input_str: str) -> str:
    """ユーザー入力を安全にサニタイズする"""
    return re.sub(r'[<>&\'"()]', '', input_str)

# 必要に応じて他のヘルパー関数を追加