"""AtHand 入口：初始化 QApplication、热键、托盘、窗口"""

import sys
import os

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

# 确保 src 目录在模块搜索路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import load_config
from core.hotkey import HotkeyManager
from core.tray import SystemTray
from ui.spotlight import SpotlightWindow


def check_macos_permission():
    """macOS 上检查辅助功能权限"""
    if sys.platform != "darwin":
        return True

    try:
        from pynput import keyboard
        # 尝试创建一个 listener 来检测权限
        test_listener = keyboard.Listener(on_press=lambda k: None)
        test_listener.start()
        test_listener.stop()
        return True
    except Exception:
        return False


def main():
    # 高 DPI 缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出
    app.setApplicationName("AtHand")
    app.setApplicationDisplayName("AtHand")

    # 加载配置
    config = load_config()

    # 创建主窗口
    spotlight = SpotlightWindow(config)

    # macOS 权限检查
    if sys.platform == "darwin" and not check_macos_permission():
        QMessageBox.warning(
            None,
            "需要辅助功能权限",
            "AtHand 需要辅助功能权限才能检测全局快捷键。\n\n"
            "请在 系统设置 > 隐私与安全 > 辅助功能 中\n"
            "授权 AtHand，然后重新启动应用。",
        )

    # 创建热键管理器
    hotkey = HotkeyManager()
    hotkey.triggered.connect(spotlight.toggle_visibility)
    hotkey.permission_warning.connect(
        lambda msg: QMessageBox.warning(None, "权限警告", msg)
    )
    hotkey.start()

    # 创建系统托盘
    tray = SystemTray(spotlight, config)
    tray.show()

    # 首次启动提示
    if not config.get("api_key"):
        # 延迟显示，确保托盘已就绪
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: (
            spotlight.show_window(),
            spotlight.show_settings(),
        ))

    exit_code = app.exec()

    # 清理
    hotkey.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()