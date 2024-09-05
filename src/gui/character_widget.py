"""
キャラクター表示ウィジェット

役割:
- キャラクター画像の表示と管理
- タイマーの状態に応じたキャラクターの表情/姿勢の変更

主な機能:
- 透過PNG画像の表示
- アニメーション効果（状態変化時のスムーズな遷移）

使用するクラス/モジュール:
- core.character_state.CharacterState
- utils.ui_helpers

注意点:
- 画像リソースの効率的な管理（メモリ使用量に注意）
- スムーズなアニメーション処理（パフォーマンスに注意）
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap
from src.utils.ui_helpers import load_pixmap

class CharacterWidget(QLabel):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.character_state = None
        self.current_pixmap = None
        self.setup_ui()

    def setup_ui(self):
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 200)
        self.load_default_image()

    def load_default_image(self):
        default_image = self.config.get('default_character_image', 'resources/images/character_neutral.png')
        self.set_image(default_image)

    def set_image(self, image_path):
        pixmap = load_pixmap(image_path)
        if pixmap:
            self.current_pixmap = pixmap
            self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_character_state(self, mood, pose):
        image_path = f"resources/images/character_{mood.value}_{pose.value}.png"
        self.animate_transition(image_path)

    def animate_transition(self, new_image_path):
        new_pixmap = load_pixmap(new_image_path)
        if new_pixmap:
            self.animation = QPropertyAnimation(self, b"pixmap")
            self.animation.setDuration(500)  # 500ミリ秒でアニメーション
            self.animation.setStartValue(self.current_pixmap)
            self.animation.setEndValue(new_pixmap)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.start()

    def adjust_size(self, parent_size):
        new_size = min(parent_size.width(), parent_size.height()) * 0.6
        self.setFixedSize(new_size, new_size)
        if self.current_pixmap:
            self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap:
            self.setPixmap(self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))