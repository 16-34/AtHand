"""QSS 样式常量：暗色毛玻璃主题"""

# 窗口尺寸
WINDOW_WIDTH = 640
SEARCH_BAR_HEIGHT = 52
ANSWER_PANEL_MAX_HEIGHT = 400
BORDER_RADIUS = 14

# 颜色常量
COLORS = {
    "bg_primary": "#1e1e2e",       # 主背景（深色）
    "bg_secondary": "#2a2a3c",     # 输入框背景
    "bg_input": "#33334d",          # 输入框激活背景
    "text_primary": "#e0e0e0",      # 主文字
    "text_secondary": "#8888a0",    # 次要文字
    "text_placeholder": "#666688",  # 占位文字
    "accent": "#7c6ff7",            # 强调色（紫蓝）
    "accent_hover": "#9580ff",      # 强调色悬浮
    "border": "#3a3a55",            # 边框色
    "error": "#f38ba8",             # 错误红
    "success": "#a6e3a1",           # 成功绿
}

# 主窗口样式
SPOTLIGHT_STYLESheet = f"""
QWidget#spotlight {{
    background: transparent;
}}

QWidget#container {{
    background: rgba(30, 30, 46, 230);
    border: 1px solid {COLORS['border']};
    border-radius: {BORDER_RADIUS}px;
}}

QLineEdit#search_input {{
    background: transparent;
    color: {COLORS['text_primary']};
    border: none;
    font-size: 18px;
    padding: 14px 16px 14px 48px;
    selection-background-color: {COLORS['accent']};
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

QTextEdit#answer_text {{
    background: transparent;
    color: {COLORS['text_primary']};
    border: none;
    font-size: 14px;
    padding: 12px 16px;
    selection-background-color: {COLORS['accent']};
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
    color: {COLORS['text_primary']};
    font-size: 14px;
}}

QLineEdit {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    selection-background-color: {COLORS['accent']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QSlider::groove:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['accent']};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}}

QSlider::sub-page:horizontal {{
    background: {COLORS['accent']};
    border-radius: 3px;
}}

QPushButton {{
    background: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
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
}}

QPushButton#cancel_btn:hover {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QPushButton#test_btn {{
    background: transparent;
    color: {COLORS['accent']};
    border: 1px solid {COLORS['accent']};
}}

QPushButton#test_btn:hover {{
    background: {COLORS['accent']};
    color: white;
}}

QSpinBox {{
    background: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}}
"""

# 设置按钮图标按钮样式（用于搜索栏内的设置图标）
SETTINGS_BTN_STYLE = f"""
QPushButton#settings_btn {{
    background: transparent;
    border: none;
    color: {COLORS['text_secondary']};
    font-size: 18px;
    padding: 4px 8px;
    border-radius: 6px;
}}

QPushButton#settings_btn:hover {{
    background: rgba(255, 255, 255, 30);
    color: {COLORS['text_primary']};
}}
"""