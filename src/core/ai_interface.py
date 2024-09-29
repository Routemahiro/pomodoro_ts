"""
AI (ChatGPT) とのインターフェース

役割:
- ChatGPT APIとの通信
- AIの応答の解析とタスク分解

主な機能:
- APIリクエストの送信と応答の受信
- 応答のJSON解析とタスクデータへの変換

使用するクラス/モジュール:
- utils.config.Config
- data.ai_conversation.AIConversation

注意点:
- API呼び出しの頻度制限に注意
- APIキーの安全な管理（設定ファイルからの読み込み、暗号化など）
- ネットワークエラーなどの例外処理を適切に行うこと
"""

import requests
import json
from typing import List, Dict
from src.utils.config import config
from src.data.ai_conversation import AIConversationManager
from cryptography.fernet import Fernet

class AIInterface:
    def __init__(self, config, ai_conversation_manager: AIConversationManager):
        self.config = config
        self.ai_conversation_manager = ai_conversation_manager
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _get_api_key(self):
        api_key = self.config.get('openai_api_key')
        if not api_key:
            print("APIキーが設定されていません。")
            return None

        encryption_key = self.config.get('encryption_key')
        if not encryption_key:
            print("暗号化キーが設定されていません。")
            return None

        try:
            fernet = Fernet(encryption_key.encode())
            encrypted_api_key = fernet.encrypt(api_key.encode())
            self.config.set('encrypted_openai_api_key', encrypted_api_key.decode())
            return api_key
        except Exception as e:
            print(f"APIキーの暗号化中にエラーが発生しました: {e}")
            return None

    def send_message(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        api_key = self._get_api_key()
        if api_key is None:
            return "APIキーが未設定だよ。OpenAI APIキーを設定してね。"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # 会話履歴の保存
            self.ai_conversation_manager.add_message(message, "user")
            self.ai_conversation_manager.add_message(ai_response, "assistant")
            
            return ai_response
        except requests.exceptions.RequestException as e:
            print(f"APIリクエスト中にエラーが発生しちゃった: {e}")
            return "ごめんね。エラーが発生しちゃったよ。"

    def analyze_tasks(self, task_description: str) -> List[Dict[str, str]]:
        prompt = f"以下のタスク説明を個別のサブタスクに分解してください。JSON形式で返答してください：\n{task_description}"
        response = self.send_message(prompt)
        
        try:
            tasks = json.loads(response)
            return tasks
        except json.JSONDecodeError:
            print("AIの応答をJSONとして解析できませんでした。")
            return []

    def get_productivity_tips(self) -> str:
        prompt = "生産性を向上させるためのヒントを3つ教えてください。"
        return self.send_message(prompt)

    def get_task_prioritization(self, tasks: List[str]) -> List[str]:
        task_list = "\n".join(tasks)
        prompt = f"以下のタスクリストを優先順位順に並べ替えてください：\n{task_list}"
        response = self.send_message(prompt)
        return response.split("\n")