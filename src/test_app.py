import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from src.utils.config import config
from src.utils.constants import TimerDefaults, Colors
from src.utils.ui_helpers import create_button, create_label, load_pixmap
from src.utils.helpers import format_time, generate_unique_id

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("テストアプリケーション")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 設定のテスト
        work_time = TimerDefaults.WORK_TIME.value
        layout.addWidget(QLabel(f"作業時間: {format_time(work_time)}"))

        # UIヘルパーのテスト
        test_button = create_button("テストボタン", style_class="primary")
        layout.addWidget(test_button)

        test_label = create_label("テストラベル", style_class="info")
        layout.addWidget(test_label)

        # ヘルパー関数のテスト
        unique_id = generate_unique_id()
        layout.addWidget(QLabel(f"生成されたID: {unique_id}"))

        # 設定変更のテスト
        self.color_label = QLabel(f"現在の色: {Colors.PRIMARY.value}")
        layout.addWidget(self.color_label)

        change_color_button = QPushButton("色を変更")
        change_color_button.clicked.connect(self.change_color)
        layout.addWidget(change_color_button)

    def change_color(self):
        new_color = "#FF5733"  # 新しい色
        config.set('color_primary', new_color)
        self.color_label.setText(f"現在の色: {Colors.PRIMARY.value}")

def main():
    app = QApplication(sys.argv)

    # スタイルシートの適用
    with open("resources/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())

    config.load()  # 設定のロード
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()