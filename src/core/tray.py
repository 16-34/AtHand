"""系统托盘图标 + 菜单"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor


def _create_default_icon() -> QIcon:
    """生成默认托盘图标（蓝色圆形）"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(52, 152, 219))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawEllipse(4, 4, 56, 56)
    # 绘制 A 字母
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setPixelSize(36)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x0084, "A")  # Qt.AlignCenter
    painter.end()
    return QIcon(pixmap)


class SystemTray:
    """系统托盘管理"""

    def __init__(self, spotlight_window, config=None):
        self.spotlight = spotlight_window
        self.config = config
        self._icon = self._load_icon()
        self._tray = QSystemTrayIcon(self._icon)
        self._tray.setToolTip("AtHand - 双击 Shift 唤起")
        self._build_menu()

    def _load_icon(self) -> QIcon:
        """尝试加载图标文件，失败则使用默认图标"""
        # 尝试从资源目录加载
        resource_dir = Path(__file__).parent.parent / "resources"
        for name in ("icon.png", "icon.icns"):
            icon_path = resource_dir / name
            if icon_path.exists():
                return QIcon(str(icon_path))
        return _create_default_icon()

    def _build_menu(self):
        """构建托盘菜单"""
        menu = QMenu()

        show_action = menu.addAction("显示搜索栏")
        show_action.triggered.connect(self._show_spotlight)

        menu.addSeparator()

        settings_action = menu.addAction("设置...")
        settings_action.triggered.connect(self._open_settings)

        menu.addSeparator()

        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit)

        self._tray.setContextMenu(menu)

        # 双击托盘图标也可切换窗口
        self._tray.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        """托盘图标激活回调"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_spotlight()

    def _show_spotlight(self):
        """显示搜索栏（始终置于前台）"""
        self.spotlight.bring_to_front()

    def _open_settings(self):
        """打开设置界面"""
        self.spotlight.show_settings()

    def _quit(self):
        """退出应用"""
        from PySide6.QtWidgets import QApplication
        QApplication.instance().quit()

    def show(self):
        """显示托盘图标"""
        self._tray.show()