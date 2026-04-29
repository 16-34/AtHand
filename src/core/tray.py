"""系统托盘图标 + 菜单"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt, QRectF


def _create_default_icon() -> QIcon:
    """生成简约托盘图标：深灰圆角方块 + 白色上箭头"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 圆角方块背景
    rect = QRectF(4, 4, 56, 56)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1a1a1a"))
    p.drawRoundedRect(rect, 14, 14)

    # 白色上箭头（代表"唤起"）
    pen = QPen(QColor("#ffffff"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # 箭头竖线
    p.drawLine(32, 48, 32, 22)
    # 箭头头部
    p.drawLine(22, 30, 32, 20)
    p.drawLine(42, 30, 32, 20)

    # 底部装饰线
    pen2 = QPen(QColor(255, 255, 255, 100), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen2)
    p.drawLine(24, 52, 40, 52)

    p.end()
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
        """尝试加载图标文件，失败则使用代码生成的图标"""
        resource_dir = Path(__file__).parent.parent / "resources"
        # 优先加载 SVG / PNG
        for name in ("icon.svg", "icon.png", "icon.icns"):
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

    def hide(self):
        """隐藏托盘图标（退出前清理）"""
        self._tray.hide()