"""主浮动窗口：Spotlight 风格搜索栏 + 回答面板"""

import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeyEvent, QFont

from ui.answer_panel import AnswerPanel
from ui.settings_dialog import SettingsDialog
from ui.styles import (
    SPOTLIGHT_STYLESheet, SETTINGS_BTN_STYLE,
    WINDOW_WIDTH, SEARCH_BAR_HEIGHT, ANSWER_PANEL_MAX_HEIGHT,
    MARGIN, COLORS,
)
from core.config import load_config, save_config
from core.llm import ChatSession


class SpotlightWindow(QWidget):
    """Spotlight 风格主窗口

    搜索态：仅显示搜索栏（640×52）
    回答态：展开搜索栏+回答面板（640×~450）
    """

    settings_changed = Signal(dict)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self.setObjectName("spotlight")
        self._is_visible = False
        self._answer_expanded = False
        self._hotkey_manager = None

        # 会话管理
        self.chat_session = ChatSession(self.config)
        self.chat_session.chunk_received.connect(self._on_chunk_received)
        self.chat_session.response_finished.connect(self._on_response_finished)
        self.chat_session.error_occurred.connect(self._on_error)

        self._setup_window()
        self._setup_ui()
        self._apply_styles()

    def _setup_window(self):
        """配置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._collapsed_height = SEARCH_BAR_HEIGHT + MARGIN * 2
        self._expanded_height = SEARCH_BAR_HEIGHT + ANSWER_PANEL_MAX_HEIGHT + MARGIN * 2

        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(self._collapsed_height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _setup_ui(self):
        """构建 UI"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        outer_layout.setSpacing(0)

        self.container = QWidget()
        self.container.setObjectName("container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        # 输入框（无搜索图标）
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Ask anything...")
        self.search_input.setFont(QFont("Helvetica Neue", 18))
        self.search_input.returnPressed.connect(self._on_submit)
        search_layout.addWidget(self.search_input)

        # 设置按钮
        self.settings_btn = QPushButton("...")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setFixedSize(40, SEARCH_BAR_HEIGHT)
        self.settings_btn.clicked.connect(self.show_settings)
        search_layout.addWidget(self.settings_btn)

        self.container_layout.addLayout(search_layout)

        # 回答面板（初始隐藏）
        self.answer_panel = AnswerPanel()
        self.answer_panel.setVisible(False)
        self.container_layout.addWidget(self.answer_panel)

        outer_layout.addWidget(self.container)

    def _apply_styles(self):
        self.setStyleSheet(SPOTLIGHT_STYLESheet + SETTINGS_BTN_STYLE)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 3 - self.height() // 2
        self.move(x, y)

    # ---- 事件处理 ----

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_window()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._answer_expanded:
            QTimer.singleShot(50, self.search_input.setFocus)

    # ---- 公共方法 ----

    def toggle_visibility(self):
        if self.isVisible():
            self.hide_window()
        else:
            self.show_window()

    def bring_to_front(self):
        self.show_window()

    def show_window(self):
        self._is_visible = True
        if sys.platform == "darwin":
            try:
                from AppKit import NSApp
                NSApp.activateIgnoringOtherApps_(True)
            except ImportError:
                pass
        QTimer.singleShot(50, self._do_show)

    def _do_show(self):
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if not self._answer_expanded:
            self.search_input.setFocus()

    def hide_window(self):
        self._is_visible = False
        self.chat_session.clear()
        self.answer_panel.clear()
        self.answer_panel.setVisible(False)
        self._answer_expanded = False
        self.search_input.clear()
        self.setFixedHeight(self._collapsed_height)
        self.hide()

    def set_hotkey_manager(self, manager):
        self._hotkey_manager = manager

    def show_settings(self):
        if self._hotkey_manager:
            self._hotkey_manager.pause()
        dialog = SettingsDialog(self.config, self)
        result = dialog.exec()
        if self._hotkey_manager:
            self._hotkey_manager.resume()
        if result == SettingsDialog.DialogCode.Accepted:
            self.config = load_config()
            self.chat_session.update_config(self.config)
            self.settings_changed.emit(self.config)

    # ---- 内部方法 ----

    def _on_submit(self):
        query = self.search_input.text().strip()
        if not query:
            return
        if self.chat_session.is_busy():
            return

        if not self._answer_expanded:
            self._answer_expanded = True
            self.answer_panel.setVisible(True)
            self.setFixedHeight(self._expanded_height)

        self.answer_panel.add_user_message(query)
        self.answer_panel.start_streaming()
        self.search_input.setEnabled(False)

        self.chat_session.send(query)

    def _on_chunk_received(self, chunk: str):
        self.answer_panel.append_chunk(chunk)

    def _on_response_finished(self, full_response: str):
        self.answer_panel.finish_streaming(full_response)
        self.search_input.setEnabled(True)
        self.search_input.setFocus()
        self.search_input.clear()

    def _on_error(self, error_msg: str):
        self.answer_panel.show_error(error_msg)
        self.search_input.setEnabled(True)
        self.search_input.setFocus()