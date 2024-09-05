"""
スライドインパネルの基本クラス

役割:
- 右側からスライドインするパネルの基本動作の実装

主な機能:
- スムーズなスライドインとスライドアウトのアニメーション
- パネルの表示/非表示の切り替え

使用するクラス/モジュール:
- utils.ui_helpers

注意点:
- アニメーションの実装には、QPropertyAnimationを使用すること
- パネルの表示状態を管理し、複数のパネルが同時に開かないようにすること
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property

class SlidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("slidePanel")
        self.setFixedWidth(300)  # パネルの幅を設定
        self.setStyleSheet("background-color: white; border-left: 1px solid #cccccc;")

        self.layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.panels = {}
        self.current_panel = None

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(300)  # アニメーションの時間（ミリ秒）

        self.hide()  # 初期状態では非表示

    def add_panel(self, name: str, panel: QWidget):
        self.panels[name] = panel
        self.stacked_widget.addWidget(panel)

    def toggle_panel(self, name: str):
        if self.current_panel == name and self.isVisible():
            self.hide_panel()
        else:
            self.show_panel(name)

    def show_panel(self, name: str):
        if name in self.panels:
            self.stacked_widget.setCurrentWidget(self.panels[name])
            self.current_panel = name
            self.show()
            self.animate_slide(True)

    def hide_panel(self):
        self.animate_slide(False)

    def animate_slide(self, show: bool):
        start = self.parent().width() if show else self.x()
        end = self.parent().width() - self.width() if show else self.parent().width()

        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

        if not show:
            self.animation.finished.connect(self.hide)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isVisible():
            self.move(self.parent().width() - self.width(), 0)