"""AtHand 入口：初始化 QApplication、热键、托盘、窗口"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import load_config
from core.hotkey import HotkeyManager
from core.tray import SystemTray
from ui.spotlight import SpotlightWindow


LOCK_FILE = os.path.join(tempfile.gettempdir(), "athand.lock")
_lock_fd = None


def acquire_lock():
    """单实例锁：如果已有实例运行则返回 False"""
    global _lock_fd
    try:
        if sys.platform == "win32":
            import msvcrt
            _lock_fd = open(LOCK_FILE, "w")
            _lock_fd.write(str(os.getpid()))
            _lock_fd.flush()
            msvcrt.locking(_lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        else:
            import fcntl
            _lock_fd = open(LOCK_FILE, "w")
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _lock_fd.write(str(os.getpid()))
            _lock_fd.flush()
            return True
    except (OSError, IOError):
        return False


def check_macos_permission():
    """macOS 上检查辅助功能权限"""
    if sys.platform != "darwin":
        return True

    try:
        from pynput import keyboard
        test_listener = keyboard.Listener(on_press=lambda k: None)
        test_listener.start()
        test_listener.stop()
        return True
    except Exception:
        return False


def main():
    # 单实例检测
    if not acquire_lock():
        print("AtHand 已在运行中")
        sys.exit(0)

    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt

    # 高 DPI 缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("AtHand")
    app.setApplicationDisplayName("AtHand")

    # macOS: 让应用成为前台进程，确保 Tool 窗口能正常显示
    if sys.platform == "darwin":
        try:
            from AppKit import NSApp
            NSApp.setActivationPolicy_(0)
        except ImportError:
            pass

    config = load_config()
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

    hotkey = HotkeyManager()
    hotkey.triggered.connect(spotlight.toggle_visibility)
    hotkey.permission_warning.connect(
        lambda msg: QMessageBox.warning(None, "权限警告", msg)
    )
    spotlight.set_hotkey_manager(hotkey)
    hotkey.start()

    tray = SystemTray(spotlight, config)
    tray.show()

    # 首次启动引导设置
    if not config.get("api_key"):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: (
            spotlight.show_window(),
            spotlight.show_settings(),
        ))

    exit_code = app.exec()
    hotkey.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()