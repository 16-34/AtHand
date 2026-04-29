"""设置界面：API Key / 模型 / 端点配置"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QSpinBox, QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal

from openai import OpenAI, AuthenticationError, APIError

from core.config import load_config, save_config
from ui.styles import SETTINGS_STYLESheet, COLORS


class ConnectionTestWorker(QThread):
    """后台测试 API 连接"""

    finished = Signal(bool, str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            api_key = self.config.get("api_key", "")
            api_base = self.config.get("api_base", "https://api.openai.com/v1")
            model = self.config.get("model", "gpt-4o-mini")

            if not api_key:
                self.finished.emit(False, "请填写 API Key")
                return

            client = OpenAI(api_key=api_key, base_url=api_base)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0,
            )
            content = response.choices[0].message.content or "(空回复)"
            self.finished.emit(True, f"连接成功，模型回复: {content[:50]}")
        except AuthenticationError:
            self.finished.emit(False, "认证失败：API Key 无效")
        except APIError as e:
            self.finished.emit(False, f"连接失败: {str(e)[:100]}")
        except Exception as e:
            self.finished.emit(False, f"连接失败: {str(e)[:100]}")


class SettingsDialog(QDialog):
    """设置界面 — 简约黑白"""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self._test_worker = None

        self.setWindowTitle("Settings")
        self.setMinimumWidth(460)
        self.setStyleSheet(SETTINGS_STYLESheet)
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(28, 28, 28, 28)

        # 标题
        title = QLabel("Settings")
        title.setObjectName("section_title")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {COLORS['text_primary']};"
            f"padding: 0 0 20px 0; border: none;"
        )
        layout.addWidget(title)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px; border: none; margin: 0 0 16px 0;")
        layout.addWidget(line)

        # API 连接
        conn_title = QLabel("API 连接")
        conn_title.setObjectName("section_title")
        layout.addWidget(conn_title)
        layout.addSpacing(10)

        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText("https://api.openai.com/v1")
        layout.addWidget(self.api_base_input)
        layout.addSpacing(8)

        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        key_row.addWidget(self.api_key_input)

        self.toggle_key_btn = QPushButton("Show")
        self.toggle_key_btn.setObjectName("toggle_key_btn")
        self.toggle_key_btn.setFixedWidth(56)
        self.toggle_key_btn.clicked.connect(self._toggle_key_visibility)
        key_row.addWidget(self.toggle_key_btn)
        layout.addLayout(key_row)
        layout.addSpacing(8)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-sonnet-4-5-20250929",
            "deepseek/deepseek-chat",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
        ])
        layout.addWidget(self.model_combo)
        layout.addSpacing(10)

        # 测试连接
        test_row = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self._test_connection)
        test_row.addWidget(self.test_btn)
        test_row.addStretch()
        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        test_row.addWidget(self.test_result_label)
        layout.addLayout(test_row)

        layout.addSpacing(16)

        # 模型参数
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"background: {COLORS['border']}; max-height: 1px; border: none; margin: 0 0 16px 0;")
        layout.addWidget(line2)

        params_title = QLabel("模型参数")
        params_title.setObjectName("section_title")
        layout.addWidget(params_title)
        layout.addSpacing(10)

        # Temperature
        temp_row = QHBoxLayout()
        temp_label = QLabel("Temperature")
        temp_label.setFixedWidth(90)
        temp_row.addWidget(temp_label)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 20)
        self.temp_slider.setValue(7)
        temp_row.addWidget(self.temp_slider)
        self.temp_label_val = QLabel("0.7")
        self.temp_label_val.setFixedWidth(32)
        self.temp_label_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label_val.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        temp_row.addWidget(self.temp_label_val)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label_val.setText(f"{v / 10:.1f}")
        )
        layout.addLayout(temp_row)
        layout.addSpacing(8)

        # Max Tokens
        token_row = QHBoxLayout()
        token_label = QLabel("Max Tokens")
        token_label.setFixedWidth(90)
        token_row.addWidget(token_label)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 32768)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setValue(4096)
        token_row.addWidget(self.max_tokens_spin)
        layout.addLayout(token_row)

        layout.addSpacing(24)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("Show")

    def _load_values(self):
        self.api_base_input.setText(self.config.get("api_base", ""))
        self.api_key_input.setText(self.config.get("api_key", ""))

        model = self.config.get("model", "gpt-4o-mini")
        idx = self.model_combo.findText(model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setCurrentText(model)

        temp = self.config.get("temperature", 0.7)
        self.temp_slider.setValue(int(temp * 10))
        self.temp_label_val.setText(f"{temp:.1f}")

        self.max_tokens_spin.setValue(self.config.get("max_tokens", 4096))

    def _collect_values(self) -> dict:
        return {
            "api_base": self.api_base_input.text().strip() or "https://api.openai.com/v1",
            "api_key": self.api_key_input.text().strip(),
            "model": self.model_combo.currentText().strip(),
            "temperature": self.temp_slider.value() / 10.0,
            "max_tokens": self.max_tokens_spin.value(),
            "hotkey": self.config.get("hotkey", "double_shift"),
            "theme": self.config.get("theme", "dark"),
        }

    def _test_connection(self):
        values = self._collect_values()
        if not values["api_key"]:
            self.test_result_label.setText("请先填写 API Key")
            self.test_result_label.setStyleSheet(f"color: {COLORS['error']};")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.test_result_label.setText("")
        self.test_result_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self._test_worker = ConnectionTestWorker(values)
        self._test_worker.finished.connect(self._on_test_finished)
        self._test_worker.start()

    def _on_test_finished(self, success: bool, message: str):
        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test Connection")
        if success:
            self.test_result_label.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.test_result_label.setStyleSheet(f"color: {COLORS['error']};")
        self.test_result_label.setText(message)

    def _save(self):
        values = self._collect_values()
        self.config.update(values)
        save_config(self.config)
        self.accept()