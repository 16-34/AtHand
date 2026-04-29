"""全局热键管理：pynput 双击 Shift 检测"""

import time
from pynput import keyboard

from PySide6.QtCore import QObject, Signal


class HotkeyManager(QObject):
    """双击 Shift 全局热键检测器

    监听 Shift 按键，两次按下间隔 < 300ms 即触发回调。
    macOS 需要辅助功能权限，检测失败时发出警告信号。
    """

    triggered = Signal()
    permission_warning = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_shift_time = 0.0
        self._double_shift_interval = 0.3  # 秒
        self._listener = None
        self._running = False

    def _on_key_press(self, key):
        """按键回调：检测双击 Shift"""
        # pynput 可能传入 Key 对象或 KeyCode 对象
        is_shift = False
        if isinstance(key, keyboard.Key):
            is_shift = key == keyboard.Key.shift
        elif isinstance(key, keyboard.KeyCode):
            is_shift = key.char in ('Shift', 'Shift_L', 'Shift_R')
            # 某些平台上 shift 按键的 char 可能为 None
            if key.vk is not None:
                # Windows 虚拟键码：VK_LSHIFT=0xA0, VK_RSHIFT=0xA1
                is_shift = is_shift or key.vk in (0xA0, 0xA1)

        if not is_shift:
            return

        now = time.monotonic()
        if now - self._last_shift_time < self._double_shift_interval:
            self._last_shift_time = 0.0  # 重置，防止三击重复触发
            self.triggered.emit()
        else:
            self._last_shift_time = now

    def _on_key_release(self, key):
        """按键释放回调（不做处理，仅用于完整监听）"""
        pass

    def start(self):
        """启动热键监听"""
        if self._running:
            return
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
            )
            self._listener.start()
            self._running = True
        except Exception as e:
            error_msg = str(e)
            if "access" in error_msg.lower() or "permission" in error_msg.lower():
                self.permission_warning.emit(
                    "需要辅助功能权限：请在 系统设置 > 隐私与安全 > 辅助功能 中授权 AtHand"
                )
            else:
                self.permission_warning.emit(f"热键启动失败: {error_msg}")

    def stop(self):
        """停止热键监听"""
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._running = False