"""
UI関連のヘルパー関数

役割:
- GUI開発に関する汎用的な関数を提供

主な機能:
- カスタムウィジェットの作成
- アイコンやスタイルの適用
- レイアウト調整ユーティリティ

使用するクラス/モジュール:
- PySide6.QtWidgets
- PySide6.QtGui

注意点:
- PySide6の機能を最大限に活用し、効率的なUI実装を支援すること
- 異なる環境（画面サイズなど）での一貫した表示を保証すること
"""
from PySide6.QtWidgets import QWidget, QPushButton, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
import os

def load_stylesheet(path: str) -> str:
    """指定されたパスからスタイルシートを読み込む"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"警告: スタイルシートファイル '{path}' が見つかりません。")
    except Exception as e:
        print(f"スタイルシートの読み込み中にエラーが発生しました: {e}")
    return ""

def create_button(text: str, icon_path: str = None, style_class: str = None) -> QPushButton:
    """カスタムボタンを作成する"""
    button = QPushButton(text)
    if icon_path:
        button.setIcon(QIcon(icon_path))
    if style_class:
        button.setProperty("class", style_class)
    return button

def create_label(text: str, style_class: str = None) -> QLabel:
    """カスタムラベルを作成する"""
    label = QLabel(text)
    if style_class:
        label.setProperty("class", style_class)
    return label

def set_widget_size(widget: QWidget, width: int, height: int):
    """ウィジェットのサイズを設定する"""
    widget.setFixedSize(width, height)

def center_widget(widget: QWidget, parent: QWidget = None):
    """ウィジェットを親ウィジェットまたは画面の中央に配置する"""
    if parent:
        geometry = parent.geometry()
    else:
        geometry = widget.screen().availableGeometry()
    x = (geometry.width() - widget.width()) // 2
    y = (geometry.height() - widget.height()) // 2
    widget.move(x, y)

def load_pixmap(path: str, width: int = None, height: int = None) -> QPixmap:
    """画像をロードし、必要に応じてリサイズする"""
    if not os.path.exists(path):
        print(f"警告: 画像ファイルが見つかりません: {path}")
        return QPixmap()
    
    pixmap = QPixmap(path)
    if pixmap.isNull():
        print(f"警告: 画像の読み込みに失敗しました: {path}")
        return QPixmap()
    
    if width and height:
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pixmap

# 必要に応じて他のUI関連ヘルパー関数を追加