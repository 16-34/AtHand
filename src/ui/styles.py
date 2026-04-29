"""QSS 样式常量：简约黑白主题"""

# 窗口尺寸
WINDOW_WIDTH = 640
SEARCH_BAR_HEIGHT = 52
ANSWER_PANEL_MAX_HEIGHT = 400
MARGIN = 8  # 外层边距
BORDER_RADIUS = 14

# 颜色常量 — 简约黑白
COLORS = {
    "bg_primary": "#1a1a1a",       # 主背景（纯黑偏灰）
    "bg_secondary": "#262626",      # 输入框/卡片背景
    "bg_input": "#2e2e2e",          # 输入框激活背景
    "text_primary": "#ffffff",      # 主文字（纯白）
    "text_secondary": "#888888",   # 次要文字
    "text_placeholder": "#555555", # 占位文字
    "accent": "#ffffff",            # 强调色（白）
    "accent_hover": "#cccccc",      # 强调色悬浮
    "border": "#333333",            # 边框色
    "error": "#ff6b6b",             # 错误红
    "success": "#6bcb77",           # 成功绿
}

# 主窗口样式
SPOTLIGHT_STYLESheet = f"""
QWidget#spotlight {{
    background: transparent;
}}

QWidget#container {{
    background: rgba(26, 26, 26, 240);
    border: 1px solid {COLORS['border']};
    border-radius: {BORDER_RADIUS}px;
}}

QLineEdit#search_input {{
    background: transparent;
    color: {COLORS['text_primary']};
    border: none;
    border-bottom: 1px solid transparent;
    font-size: 18px;
    padding: 14px 16px;
    selection-background-color: rgba(255, 255, 255, 40);
}}

QLineEdit#search_input:focus {{
    border-bottom: 1px solid {COLORS['text_secondary']};
}}

QLineEdit#search_input::placeholder {{
    color: {COLORS['text_placeholder']};
}}
"""

# 回答面板样式
ANSWER_PANEL_STYLESheet = f"""
QWidget#answer_panel {{
    background: transparent;
    border-top: 1px solid {COLORS['border']};
}}

QLabel#status_label {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    padding: 4px 16px 8px;
}}
"""

# 设置界面样式
SETTINGS_STYLESheet = f"""
QDialog {{
    background: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

QLabel {{
    color: {COLORS['text_secondary']};
    font-size: 13px;
}}

QLabel#section_title {{
    color: {COLORS['text_primary']};
    font-size: 15px;
    font-weight: bold;
    padding: 8px 0 4px 0;
}}

QLineEdit {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: rgba(255, 255, 255, 30);
}}

QLineEdit:focus {{
    border-color: {COLORS['text_secondary']};
}}

QComboBox {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: rgba(255, 255, 255, 30);
}}

QSlider::groove:horizontal {{
    background: {COLORS['border']};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['text_primary']};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

QSlider::sub-page:horizontal {{
    background: {COLORS['text_secondary']};
    border-radius: 2px;
}}

QSpinBox {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 14px;
}}

QPushButton {{
    background: {COLORS['text_primary']};
    color: {COLORS['bg_primary']};
    border: none;
    border-radius: 6px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: bold;
}}

QPushButton:hover {{
    background: {COLORS['accent_hover']};
}}

QPushButton#cancel_btn {{
    background: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    padding: 10px 28px;
}}

QPushButton#cancel_btn:hover {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QPushButton#test_btn {{
    background: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['text_secondary']};
    padding: 8px 20px;
}}

QPushButton#test_btn:hover {{
    background: {COLORS['text_primary']};
    color: {COLORS['bg_primary']};
}}

QPushButton#toggle_key_btn {{
    background: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
}}

QPushButton#toggle_key_btn:hover {{
    color: {COLORS['text_primary']};
}}
"""

# 设置按钮样式（搜索栏内的齿轮图标）
SETTINGS_BTN_STYLE = f"""
QPushButton#settings_btn {{
    background: transparent;
    border: none;
    color: {COLORS['text_secondary']};
    font-size: 16px;
    padding: 6px 10px;
    border-radius: 6px;
}}

QPushButton#settings_btn:hover {{
    background: rgba(255, 255, 255, 20);
    color: {COLORS['text_primary']};
}}
"""