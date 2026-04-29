"""回答面板：QWebEngineView + KaTeX 渲染多轮对话历史"""

import json

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView

from ui.styles import ANSWER_PANEL_STYLESheet, COLORS
from ui.markdown_renderer import render_markdown


# 答复区域 HTML 模板，内含 KaTeX（CDN）
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: {bg};
    color: {fg};
    font-family: "Helvetica Neue", -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    line-height: 1.7;
    padding: 12px 16px 4px 16px;
    overflow-y: auto;
    overflow-x: hidden;
}}
#content {{ word-wrap: break-word; }}
#content pre {{
    background: rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 10px 14px;
    overflow-x: auto;
    margin: 8px 0;
    font-size: 13px;
}}
#content code {{
    background: rgba(255,255,255,0.08);
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 13px;
}}
#content pre code {{
    background: transparent;
    padding: 0;
}}
#content p {{ margin: 6px 0; }}
#content ul, #content ol {{ margin: 6px 0; padding-left: 20px; }}
#content blockquote {{
    border-left: 3px solid {accent};
    padding-left: 12px;
    margin: 8px 0;
    color: {muted};
}}
#content table {{
    border-collapse: collapse;
    margin: 8px 0;
    width: 100%;
}}
#content th, #content td {{
    border: 1px solid {border};
    padding: 6px 10px;
    text-align: left;
}}
#content th {{
    background: rgba(255,255,255,0.06);
}}
.user-msg {{
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    margin: 14px 0 2px 0;
    font-size: 13px;
    letter-spacing: 0.02em;
    padding-left: 10px;
    border-left: 2px solid rgba(255,255,255,0.3);
}}
.user-msg:first-child {{ margin-top: 0; }}
.status-line {{
    color: {muted};
    font-size: 12px;
    padding: 4px 0;
}}
.katex-display {{ margin: 10px 0; }}
</style>
</head>
<body>
<div id="content"></div>
<script>
const KATEX_CONFIG = {{
    delimiters: [
        {{left: '$$', right: '$$', display: true}},
        {{left: '$', right: '$', display: false}},
        {{left: '\\\\(', right: '\\\\)', display: false}},
        {{left: '\\\\[', right: '\\\\]', display: true}},
    ],
    throwOnError: false
}};

function updateContent(html, scroll) {{
    var el = document.getElementById('content');
    el.innerHTML = html;
    if (typeof renderMathInElement !== 'undefined') {{
        renderMathInElement(el, KATEX_CONFIG);
    }}
    if (scroll) {{
        window.scrollTo(0, document.body.scrollHeight);
    }}
}}

function scrollToEnd() {{
    window.scrollTo(0, document.body.scrollHeight);
}}
</script>
</body>
</html>"""


class AnswerPanel(QWidget):
    """流式回答显示面板

    使用 QWebEngineView 渲染 Markdown + LaTeX 公式，
    支持多轮对话历史显示。
    """

    copy_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("answer_panel")
        self.setStyleSheet(ANSWER_PANEL_STYLESheet)

        self._is_streaming = False
        self._stream_buffer = ""  # 当前流式回答的文本
        self._history_parts: list[str] = []  # 已完成的历史片段 HTML
        self._page_ready = False

        self._setup_ui()

        # 防抖：流式更新时每 80ms 合并渲染一次
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(80)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._flush_update)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # WebEngine 视图
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background: transparent;")
        self.web_view.page().loadFinished.connect(self._on_page_loaded)

        # 加载 HTML 模板
        bg = COLORS["bg_primary"]
        fg = COLORS["text_primary"]
        accent = COLORS["accent"]
        muted = COLORS["text_secondary"]
        border = COLORS["border"]
        self._html_template = HTML_TEMPLATE.format(
            bg=bg, fg=fg, accent=accent, muted=muted, border=border,
        )
        self.web_view.setHtml(self._html_template, baseUrl="https://athand.local")

        layout.addWidget(self.web_view, 1)

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

    def _on_page_loaded(self, ok):
        """页面加载完成（KaTeX 就绪）"""
        self._page_ready = ok
        if ok and self._history_parts:
            self._render_content()

    def _build_html(self, extra: str = "") -> str:
        """拼接历史 + 当前流式内容为完整 HTML"""
        parts = list(self._history_parts)
        if extra:
            # 流式内容先做 Markdown 转换
            parts.append(render_markdown(extra))
        return "\n".join(parts)

    def _render_content(self, scroll: bool = True):
        """通过 JS 更新页面内容"""
        if not self._page_ready:
            return
        html = self._build_html(extra=self._stream_buffer if self._is_streaming else "")
        js = f"updateContent({json.dumps(html)}, {str(scroll).lower()})"
        self.web_view.page().runJavaScript(js)

    def _flush_update(self):
        """防抖定时器触发：实际执行渲染"""
        self._render_content(scroll=True)

    def _schedule_update(self):
        """安排一次防抖渲染"""
        if not self._update_timer.isActive():
            self._update_timer.start()

    # ---- 公共接口 ----

    def add_user_message(self, message: str):
        """在面板中追加用户提问"""
        self._history_parts.append(
            f'<div class="user-msg">{self._escape_html(message)}</div>'
        )
        self._render_content(scroll=True)

    def start_streaming(self):
        """开始流式接收"""
        self._is_streaming = True
        self._stream_buffer = ""
        self.status_label.setText("思考中...")
        self.status_label.setStyleSheet(f"color: {COLORS['accent']};")
        self.hint_label.setVisible(False)

    def append_chunk(self, chunk: str):
        """追加一个文本块（防抖渲染）"""
        self._stream_buffer += chunk
        self.status_label.setText("回答中...")
        self._schedule_update()

    def finish_streaming(self, full_response: str):
        """流式传输结束"""
        self._is_streaming = False
        # 将完成的回答加入历史
        self._history_parts.append(render_markdown(full_response))
        self._stream_buffer = ""
        self._update_timer.stop()
        self._render_content(scroll=True)
        self.status_label.setText("")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.hint_label.setVisible(True)

    def show_error(self, error_msg: str):
        """显示错误信息"""
        self._is_streaming = False
        self._stream_buffer = ""
        self._update_timer.stop()
        self._history_parts.append(
            f'<div style="color: {COLORS["error"]}">⚠️ {self._escape_html(error_msg)}</div>'
        )
        self._render_content(scroll=True)
        self.status_label.setText("出错了")
        self.hint_label.setVisible(True)

    def clear(self):
        """清空内容"""
        self._stream_buffer = ""
        self._history_parts.clear()
        self._is_streaming = False
        self._update_timer.stop()
        self._render_content(scroll=False)
        self.status_label.setText("")

    @property
    def is_streaming(self) -> bool:
        return self._is_streaming

    @staticmethod
    def _escape_html(text: str) -> str:
        """转义 HTML 特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )