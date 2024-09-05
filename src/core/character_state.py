"""
キャラクターの状態管理

役割:
- キャラクターの表情や姿勢の状態管理

主な機能:
- 現在の状態の保持と更新
- 状態に応じた画像ファイル名の提供

使用するクラス/モジュール:
- utils.config.Config

注意点:
- 状態変更時にはシグナルを発行し、GUI更新を促すこと
- 存在しない状態への変更要求があった場合の適切なエラーハンドリング
"""

from enum import Enum
from src.utils.config import config

class CharacterMood(Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    TIRED = "tired"
    EXCITED = "excited"
    FOCUSED = "focused"

class CharacterPose(Enum):
    STANDING = "standing"
    SITTING = "sitting"
    WORKING = "working"
    RESTING = "resting"

class CharacterState:
    def __init__(self, config):
        self.config = config
        self.mood = CharacterMood.NEUTRAL
        self.pose = CharacterPose.STANDING
        self.observers = []

    def set_mood(self, mood: CharacterMood):
        if not isinstance(mood, CharacterMood):
            raise ValueError("無効な気分状態です。")
        self.mood = mood
        self._notify_observers()

    def set_pose(self, pose: CharacterPose):
        if not isinstance(pose, CharacterPose):
            raise ValueError("無効なポーズ状態です。")
        self.pose = pose
        self._notify_observers()

    def get_image_filename(self) -> str:
        return f"{self.mood.value}_{self.pose.value}.png"

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def _notify_observers(self):
        for observer in self.observers:
            observer(self.mood, self.pose)

    def update_state_based_on_timer(self, timer_type, remaining_time):
        if timer_type == "WORK":
            if remaining_time > self.config.get('work_time', 25 * 60) * 0.8:
                self.set_mood(CharacterMood.EXCITED)
                self.set_pose(CharacterPose.WORKING)
            elif remaining_time > self.config.get('work_time', 25 * 60) * 0.2:
                self.set_mood(CharacterMood.FOCUSED)
                self.set_pose(CharacterPose.WORKING)
            else:
                self.set_mood(CharacterMood.TIRED)
                self.set_pose(CharacterPose.WORKING)
        elif timer_type in ["SHORT_BREAK", "LONG_BREAK"]:
            self.set_mood(CharacterMood.HAPPY)
            self.set_pose(CharacterPose.RESTING)