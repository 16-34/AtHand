"""回答面板：流式 Markdown 渲染区域"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor

from ui.styles import ANSWER_PANEL_STYLESheet, COLORS


class AnswerPanel(QWidget):
    """流式回答显示面板

    接收 LLM 逐 chunk 推送的文本，实时渲染为 Markdown。
    """

    copy_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("answer_panel")
        self.setStyleSheet(ANSWER_PANEL_STYLESheet)

        self._is_streaming = False
        self._full_text = ""

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 回答文本区域
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("answer_text")
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("system-ui", 14))
        self.text_edit.setFrameShape(QTextEdit.Shape.NoFrame)
        # 支持 Markdown 基础渲染
        self.text_edit.setMarkdown("")
        # 隐藏滚动条但可以滚动
        self.text_edit.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.text_edit.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        layout.addWidget(self.text_edit)

        # 底部状态栏
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(16, 0, 16, 8)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.hint_label = QLabel("Esc 关闭")
        self.hint_label.setObjectName("status_label")
        status_layout.addWidget(self.hint_label)

        layout.addLayout(status_layout)

    def start_streaming(self):
        """开始流式接收"""
        self._is_streaming = True
        self._full_text = ""
        self.text_edit.clear()
        self.text_edit.setVisible(True)
        self.status_label.setText("思考中...")
        self.status_label.setStyleSheet(
            f"color: {COLORS['accent']};"
        )
        self.hint_label.setVisible(False)

    def append_chunk(self, chunk: str):
        """追加一个文本块"""
        self._full_text += chunk
        # 使用 setMarkdown 重新渲染全文（保证 Markdown 格式正确）
        self.text_edit.setMarkdown(self._full_text)
        # 滚动到底部
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        self.status_label.setText("回答中...")

    def finish_streaming(self):
        """流式传输结束"""
        self._is_streaming = False
        self.status_label.setText("")
        self.status_label.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        self.hint_label.setVisible(True)

    def show_error(self, error_msg: str):
        """显示错误信息"""
        self._is_streaming = False
        self.text_edit.clear()
        self.text_edit.setMarkdown(f"⚠️ {error_msg}")
        self.text_edit.setStyleSheet(
            f"color: {COLORS['error']};"
        )
        self.status_label.setText("出错了")
        self.hint_label.setVisible(True)

    def clear(self):
        """清空内容"""
        self._full_text = ""
        self.text_edit.clear()
        self.status_label.setText("")

    @property
    def is_streaming(self) -> bool:
        return self._is_streaming