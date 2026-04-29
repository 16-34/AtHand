"""主浮动窗口：Spotlight 风格搜索栏 + 回答面板"""

import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy, QApplication, QLabel,
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
        self._hotkey_manager = None  # 由 main.py 注入

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
        # 无边框、置顶、不在任务栏显示
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # 透明背景（毛玻璃效果的基础）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 搜索态高度 = 搜索栏高度 + 上下边距
        self._collapsed_height = SEARCH_BAR_HEIGHT + MARGIN * 2
        # 回答态高度
        self._expanded_height = SEARCH_BAR_HEIGHT + ANSWER_PANEL_MAX_HEIGHT + MARGIN * 2

        self.setFixedWidth(WINDOW_WIDTH)
        self.setFixedHeight(self._collapsed_height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _setup_ui(self):
        """构建 UI"""
        # 外层布局（带边距让圆角可见）
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(0)

        # 容器（带圆角背景）
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # 搜索栏行
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(8, 0, 8, 0)
        search_layout.setSpacing(0)

        # 搜索图标（用 Unicode 代替，不需要资源文件）
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(
            f"font-size: 18px; color: {COLORS['text_secondary']};"
            f"padding-left: 8px;"
        )
        search_icon.setFixedWidth(36)
        search_layout.addWidget(search_icon)

        # 输入框
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("输入你的问题... (Enter 发送)")
        self.search_input.setFont(QFont("Helvetica Neue", 18))
        self.search_input.returnPressed.connect(self._on_submit)
        search_layout.addWidget(self.search_input)

        # 设置按钮
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.clicked.connect(self.show_settings)
        search_layout.addWidget(self.settings_btn)

        self.container_layout.addLayout(search_layout)

        # 回答面板（初始隐藏）
        self.answer_panel = AnswerPanel()
        self.answer_panel.setVisible(False)
        self.container_layout.addWidget(self.answer_panel)

        outer_layout.addWidget(self.container)

    def _apply_styles(self):
        """应用 QSS 样式"""
        self.setStyleSheet(SPOTLIGHT_STYLESheet + SETTINGS_BTN_STYLE)

    def _center_on_screen(self):
        """窗口居中偏上"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 3 - self.height() // 2
        self.move(x, y)

    # ---- 事件处理 ----

    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件：Esc 关闭"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_window()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        """显示时聚焦输入框"""
        super().showEvent(event)
        if not self._answer_expanded:
            QTimer.singleShot(50, self.search_input.setFocus)

    # ---- 公共方法 ----

    def toggle_visibility(self):
        """热键切换：可见则隐藏，不可见则显示"""
        if self.isVisible():
            self.hide_window()
        else:
            self.show_window()

    def bring_to_front(self):
        """始终将窗口置于前台（用于托盘菜单）"""
        self.show_window()

    def show_window(self):
        """显示窗口"""
        self._is_visible = True
        # macOS: 必须先将应用置于前台，否则 Tool 窗口不会显示
        if sys.platform == "darwin":
            try:
                from AppKit import NSApp
                NSApp.activateIgnoringOtherApps_(True)
            except ImportError:
                pass
        # 延迟显示，等待应用激活完成后再 show
        # macOS 的 activate 是异步的，同一帧内 show 会被系统忽略
        QTimer.singleShot(50, self._do_show)

    def _do_show(self):
        """实际执行窗口显示"""
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if not self._answer_expanded:
            self.search_input.setFocus()

    def hide_window(self):
        """隐藏窗口并清空会话"""
        self._is_visible = False
        self.chat_session.clear()
        self.answer_panel.clear()
        self.answer_panel.setVisible(False)
        self._answer_expanded = False
        self.search_input.clear()
        self.setFixedHeight(self._collapsed_height)
        self.hide()

    def set_hotkey_manager(self, manager):
        """注入热键管理器，用于在对话框打开时暂停热键"""
        self._hotkey_manager = manager

    def show_settings(self):
        """打开设置界面"""
        # 暂停热键监听，防止对话框中打字触发双击 Shift
        if self._hotkey_manager:
            self._hotkey_manager.pause()
        dialog = SettingsDialog(self.config, self)
        result = dialog.exec()
        # 恢复热键监听
        if self._hotkey_manager:
            self._hotkey_manager.resume()
        if result == SettingsDialog.DialogCode.Accepted:
            self.config = load_config()
            self.chat_session.update_config(self.config)
            self.settings_changed.emit(self.config)

    # ---- 内部方法 ----

    def _on_submit(self):
        """用户按下 Enter 提交问题"""
        query = self.search_input.text().strip()
        if not query:
            return

        if self.chat_session.is_busy():
            return

        # 首次提问时展开回答面板
        if not self._answer_expanded:
            self._answer_expanded = True
            self.answer_panel.setVisible(True)
            self.setFixedHeight(self._expanded_height)

        self.answer_panel.start_streaming()
        self.search_input.setEnabled(False)

        self.chat_session.send(query)

    def _on_chunk_received(self, chunk: str):
        """收到流式文本块"""
        self.answer_panel.append_chunk(chunk)

    def _on_response_finished(self, full_response: str):
        """回答完成"""
        self.answer_panel.finish_streaming()
        self.search_input.setEnabled(True)
        self.search_input.setFocus()
        # 清空输入框，准备下一轮
        self.search_input.clear()

    def _on_error(self, error_msg: str):
        """发生错误"""
        self.answer_panel.show_error(error_msg)
        self.search_input.setEnabled(True)
        self.search_input.setFocus()