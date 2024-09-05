"""
AI会話履歴の管理

役割:
- AI（ChatGPT）との会話履歴の保存と管理

主な機能:
- 会話メッセージの保存
- 会話コンテキストの維持
- 過去の会話の検索

使用するクラス/モジュール:
- data.database.Database

注意点:
- 長期間の使用で会話履歴が肥大化しないよう、適切なデータ管理を行うこと
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import logging

@dataclass
class ConversationMessage:
    id: Optional[int]
    message: str
    role: str
    timestamp: datetime = datetime.now()

class AIConversationManager:
    def __init__(self, database):
        self.database = database

    def add_message(self, message: str, role: str) -> int:
        query = '''
            INSERT INTO ai_conversations (message, role, timestamp)
            VALUES (?, ?, ?)
        '''
        params = (message, role, datetime.now())
        return self.database.execute_insert(query, params)

    def get_conversation_history(self, limit: int = 50) -> List[ConversationMessage]:
        query = '''
            SELECT * FROM ai_conversations
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        results = self.database.execute_query(query, (limit,))
        return [ConversationMessage(**result) for result in results]

    def search_conversations(self, keyword: str) -> List[ConversationMessage]:
        query = '''
            SELECT * FROM ai_conversations
            WHERE message LIKE ?
            ORDER BY timestamp DESC
        '''
        results = self.database.execute_query(query, (f'%{keyword}%',))
        return [ConversationMessage(**result) for result in results]

    def clear_old_conversations(self, days: int = 30):
        query = '''
            DELETE FROM ai_conversations
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        '''
        deleted_count = self.database.execute_update(query, (days,))
        logging.info(f"{deleted_count}件の古い会話が削除されました。")

    def get_conversation_stats(self) -> dict:
        query = '''
            SELECT COUNT(*) as total_messages,
                   MIN(timestamp) as oldest_message,
                   MAX(timestamp) as newest_message
            FROM ai_conversations
        '''
        result = self.database.execute_query(query)[0]
        return {
            'total_messages': result['total_messages'],
            'oldest_message': result['oldest_message'],
            'newest_message': result['newest_message']
        }
