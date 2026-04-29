"""系统托盘图标 + 菜单"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PySide6.QtCore import Qt, QRectF


def _create_icon(bg_color: str, fg_color: str, fg_alpha: int = 100) -> QIcon:
    """生成托盘图标

    Args:
        bg_color: 圆角方块背景色
        fg_color: 箭头主色
        fg_alpha: 装饰线透明度 (0-255)
    """
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 圆角方块背景
    rect = QRectF(4, 4, 56, 56)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(bg_color))
    p.drawRoundedRect(rect, 14, 14)

    # 上箭头
    pen = QPen(
        QColor(fg_color), 3,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.drawLine(32, 48, 32, 22)
    p.drawLine(22, 30, 32, 20)
    p.drawLine(42, 30, 32, 20)

    # 底部装饰线
    pen2 = QPen(
        QColor(fg_color).alphaColor() if hasattr(QColor(fg_color), 'alphaColor') else QColor(fg_color),
        2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
    )
    pen2.setColor(QColor(int(QColor(fg_color).red()), int(QColor(fg_color).green()), int(QColor(fg_color).blue()), fg_alpha))
    p.setPen(pen2)
    p.drawLine(24, 52, 40, 52)

    p.end()
    return QIcon(pixmap)


def _create_dark_icon() -> QIcon:
    """暗色模式图标：深色背景 + 白色箭头"""
    return _create_icon(bg_color="#1a1a1a", fg_color="#ffffff", fg_alpha=100)


def _create_light_icon() -> QIcon:
    """亮色模式图标：浅色背景 + 深色箭头"""
    return _create_icon(bg_color="#e0e0e0", fg_color="#1a1a1a", fg_alpha=80)


def _is_dark_mode() -> bool:
    """检测系统是否为暗色模式"""
    try:
        app = QApplication.instance()
        if app:
            scheme = app.styleHints().colorScheme()
            return scheme == Qt.ColorScheme.Dark
    except Exception:
        pass
    # 默认暗色
    return True


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
        """优先加载自定义图标文件，否则根据系统主题生成"""
        resource_dir = Path(__file__).parent.parent / "resources"
        for name in ("icon.svg", "icon.png", "icon.icns"):
            icon_path = resource_dir / name
            if icon_path.exists():
                return QIcon(str(icon_path))

        # 根据系统主题生成对应图标
        if _is_dark_mode():
            return _create_dark_icon()
        else:
            return _create_light_icon()

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