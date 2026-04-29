"""回答面板：流式 Markdown 渲染区域（含多轮对话历史）"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor

from ui.styles import ANSWER_PANEL_STYLESheet, COLORS


class AnswerPanel(QWidget):
    """流式回答显示面板

    支持多轮对话历史渲染，新回答追加在历史下方。
    每一轮用户提问以加粗显示，助手回答以正文显示。
    """

    copy_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("answer_panel")
        self.setStyleSheet(ANSWER_PANEL_STYLESheet)

        self._is_streaming = False
        self._full_text = ""  # 当前流式回答的完整文本
        self._history_parts: list[str] = []  # 已完成的历史内容片段

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 回答文本区域
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("answer_text")
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Helvetica Neue", 14))
        self.text_edit.setFrameShape(QTextEdit.Shape.NoFrame)
        self.text_edit.setMarkdown("")
        # 隐藏滚动条但可以滚动
        self.text_edit.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.text_edit.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        # 自定义滚动条样式
        self.text_edit.setStyleSheet(
            ANSWER_PANEL_STYLESheet + """
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
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

    def _build_markdown(self) -> str:
        """将历史片段拼接为完整 Markdown"""
        return "\n\n".join(self._history_parts)

    def _refresh_display(self, extra: str = ""):
        """刷新显示：历史内容 + 额外追加内容"""
        full = self._build_markdown()
        if extra:
            if full:
                full += "\n\n" + extra
            else:
                full = extra
        self.text_edit.setMarkdown(full)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)

    def add_user_message(self, message: str):
        """在面板中追加用户提问（加粗显示）"""
        part = f"**🧑 {message}**"
        self._history_parts.append(part)
        self._refresh_display()

    def start_streaming(self):
        """开始流式接收新回答"""
        self._is_streaming = True
        self._full_text = ""
        self.status_label.setText("思考中...")
        self.status_label.setStyleSheet(
            f"color: {COLORS['accent']};"
        )
        self.hint_label.setVisible(False)

    def append_chunk(self, chunk: str):
        """追加一个文本块"""
        self._full_text += chunk
        # 渲染历史 + 当前流式内容
        self._refresh_display(extra=self._full_text)
        self.status_label.setText("回答中...")

    def finish_streaming(self, full_response: str):
        """流式传输结束，将回答加入历史"""
        self._is_streaming = False
        # 将完成的回答加入历史片段
        self._history_parts.append(full_response)
        self._full_text = ""
        self._refresh_display()
        self.status_label.setText("")
        self.status_label.setStyleSheet(
            f"color: {COLORS['text_secondary']};"
        )
        self.hint_label.setVisible(True)

    def show_error(self, error_msg: str):
        """显示错误信息"""
        self._is_streaming = False
        self._history_parts.append(f"⚠️ {error_msg}")
        self._refresh_display()
        self.status_label.setText("出错了")
        self.hint_label.setVisible(True)

    def clear(self):
        """清空内容"""
        self._full_text = ""
        self._history_parts.clear()
        self.text_edit.clear()
        self.status_label.setText("")

    @property
    def is_streaming(self) -> bool:
        return self._is_streaming