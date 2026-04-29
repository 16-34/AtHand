"""设置界面：API Key / 模型 / 端点配置"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QSpinBox, QFormLayout,
    QMessageBox, QApplication,
)
from PySide6.QtCore import Qt, QThread, Signal

from core.config import load_config, save_config
from ui.styles import SETTINGS_STYLESheet, COLORS


class ConnectionTestWorker(QThread):
    """后台测试 API 连接"""

    finished = Signal(bool, str)  # (success, message)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            import litellm
        except ImportError:
            self.finished.emit(False, "litellm 未安装")
            return

        try:
            api_key = self.config.get("api_key", "")
            api_base = self.config.get("api_base", "")
            model = self.config.get("model", "gpt-4o-mini")

            if not api_key:
                self.finished.emit(False, "请填写 API Key")
                return

            # 自定义 api_base 时需要 openai/ 前缀让 litellm 识别
            actual_model = model
            if api_base and api_base != "https://api.openai.com/v1":
                if not model.startswith("openai/"):
                    actual_model = f"openai/{model}"

            kwargs = {
                "model": actual_model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
                "api_key": api_key,
                "temperature": 0,
            }
            if api_base:
                kwargs["api_base"] = api_base

            response = litellm.completion(**kwargs)
            content = response.choices[0].message.content or "(空回复)"
            self.finished.emit(True, f"连接成功！模型回复: {content[:50]}")
        except litellm.AuthenticationError:
            self.finished.emit(False, "认证失败：API Key 无效")
        except Exception as e:
            self.finished.emit(False, f"连接失败: {str(e)[:100]}")


class SettingsDialog(QDialog):
    """设置界面"""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self._test_worker = None

        self.setWindowTitle("AtHand 设置")
        self.setMinimumWidth(480)
        self.setStyleSheet(SETTINGS_STYLESheet)
        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 标题
        title = QLabel("⚙️ AtHand 设置")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['accent']};")
        layout.addWidget(title)

        # 表单
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # API Base URL
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText("https://api.openai.com/v1")
        form.addRow("API 端点:", self.api_base_input)

        # API Key
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        key_layout.addWidget(self.api_key_input)

        self.toggle_key_btn = QPushButton("👁")
        self.toggle_key_btn.setFixedSize(36, 36)
        self.toggle_key_btn.setStyleSheet(
            f"background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']};"
            f"color: {COLORS['text_secondary']}; border-radius: 8px; font-size: 16px;"
        )
        self.toggle_key_btn.clicked.connect(self._toggle_key_visibility)
        key_layout.addWidget(self.toggle_key_btn)
        form.addRow("API Key:", key_layout)

        # 模型
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
        form.addRow("模型:", self.model_combo)

        # Temperature
        temp_layout = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 20)
        self.temp_slider.setValue(7)
        self.temp_label = QLabel("0.7")
        self.temp_label.setFixedWidth(40)
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label.setText(f"{v / 10:.1f}")
        )
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        form.addRow("Temperature:", temp_layout)

        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 32768)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setValue(4096)
        form.addRow("Max Tokens:", self.max_tokens_spin)

        layout.addLayout(form)

        # 连接测试按钮
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔗 测试连接")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self._test_connection)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()

        self.test_result_label = QLabel("")
        self.test_result_label.setWordWrap(True)
        test_layout.addWidget(self.test_result_label)
        layout.addLayout(test_layout)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _toggle_key_visibility(self):
        """切换 API Key 显示/隐藏"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("👁")

    def _load_values(self):
        """从配置中加载值"""
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
        self.temp_label.setText(f"{temp:.1f}")

        self.max_tokens_spin.setValue(self.config.get("max_tokens", 4096))

    def _collect_values(self) -> dict:
        """收集界面上的值"""
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
        """测试 API 连接"""
        values = self._collect_values()
        if not values["api_key"]:
            self.test_result_label.setText("⚠️ 请先填写 API Key")
            self.test_result_label.setStyleSheet(f"color: {COLORS['error']};")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        self.test_result_label.setText("")
        self.test_result_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self._test_worker = ConnectionTestWorker(values)
        self._test_worker.finished.connect(self._on_test_finished)
        self._test_worker.start()

    def _on_test_finished(self, success: bool, message: str):
        """测试完成回调"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔗 测试连接")
        if success:
            self.test_result_label.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.test_result_label.setStyleSheet(f"color: {COLORS['error']};")
        self.test_result_label.setText(message)

    def _save(self):
        """保存设置"""
        values = self._collect_values()
        self.config.update(values)
        save_config(self.config)
        self.accept()