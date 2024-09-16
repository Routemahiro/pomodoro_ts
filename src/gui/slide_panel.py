"""
スライドインパネルの基本クラス

役割:
- ウィンドウの外側にスライドアウトするパネルの動作管理。パネルの左端がメインウィンドウの右端にくっつくように表示される

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
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PySide6.QtGui import QMouseEvent

# Windows APIを使用するためのインポートを追加
import sys
if sys.platform == "win32":
    import win32gui
    import win32con

class SlidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setObjectName("slidePanel")
        self.setFixedWidth(300)  # パネルの幅を設定
        self.setStyleSheet("background-color: white; border-left: 1px solid #cccccc;")

        self.layout = QVBoxLayout(self)
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.panels = {}
        self.current_panel = None

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(300)  # アニメーションの時間（ミリ秒）

        self.hide()  # 初期状態では非表示

        self.dragging = False
        self.drag_start_position = QPoint()

    def add_panel(self, name: str, panel: QWidget):
        self.panels[name] = panel
        self.stacked_widget.addWidget(panel)

    def toggle_panel(self, name: str):
        if self.current_panel == name and self.isVisible():
            self.hide_panel()
        else:
            self.show_panel(name)

    def show_panel(self, name: str):
        print(f"Showing panel: {name}")  # デバッグ用のプリント文を追加
        if name in self.panels:
            self.stacked_widget.setCurrentWidget(self.panels[name])
            self.current_panel = name
            self.show()
            self.raise_()  # パネルを最前面に表示
            parent_rect = self.parent().geometry()
            start_rect = QRect(parent_rect.right(), parent_rect.top(), 1, parent_rect.height())
            end_rect = QRect(parent_rect.right(), parent_rect.top(), self.width(), parent_rect.height())
            self.setGeometry(start_rect)
            self.animate_slide(start_rect, end_rect)
            self.dragging = False  # パネルを表示するときにドラッグ状態をリセット
        else:
            print(f"Panel {name} not found")  # パネルが見つからない場合のエラーメッセージ

    def hide_panel(self):
        parent_rect = self.parent().geometry()
        start_rect = self.geometry()
        end_rect = QRect(parent_rect.right(), parent_rect.top(), 1, parent_rect.height())
        self.animate_slide(start_rect, end_rect)
        self.dragging = False  # パネルを隠すときにドラッグ状態をリセット

    def animate_slide(self, start_rect, end_rect):
        print(f"Animating slide: {start_rect} -> {end_rect}")  # デバッグ用のプリント文を追加
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        
        # 既存のシグナル接続を切断
        try:
            self.animation.finished.disconnect()
        except RuntimeError:
            pass  # 接続がない場合は無視
        
        if end_rect.width() == 1:
            self.animation.finished.connect(self.hide)
        else:
            self.animation.finished.connect(lambda: print("Animation finished"))  # アニメーション完了時のデバッグ出力
        
        self.animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        parent_rect = self.parent().geometry()
        self.setGeometry(parent_rect.right(), parent_rect.top(), self.width(), parent_rect.height())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def set_always_on_top(self, on_top):
        if sys.platform == "win32":
            hwnd = self.winId().__int__()
            if on_top:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)