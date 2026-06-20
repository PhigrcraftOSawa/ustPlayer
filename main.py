# main.py — ustPlayer 主入口
"""PySide6 + PySide6-Fluent-Widgets 版本，提供侧边导航的现代化界面。"""

import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    InfoBar, InfoBarPosition, MessageBox,
)

from core.log import logger
from core.settings_manager import SettingsManager
from core.ustplayer import display
import core.ustreader as ur

from ui.basic_page import BasicPage
from ui.file_page import FilePage
from ui.player_style_page import PlayerStylePage
from ui.lyric_page import LyricPage
from ui.other_page import OtherPage


class MainWindow(FluentWindow):
    """主窗口 — 侧边导航 + 堆叠页面。"""

    def __init__(self):
        super().__init__()
        self._settings = SettingsManager(self)
        self._player_window = None

        self.setWindowTitle("ustPlayer")
        self.resize(900, 620)

        icon_path = os.path.join(self._settings.program_root, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_pages()
        self._init_navigation()
        self.basic_page.set_play_callback(self._on_play)

        QTimer.singleShot(100, self._load_dropped_uplr)

    # ===================== 页面构建 =====================

    def _build_pages(self):
        self.basic_page = BasicPage(self._settings)
        self.basic_page.setObjectName("basic_page")
        self.file_page = FilePage(self._settings)
        self.file_page.setObjectName("file_page")
        self.player_style_page = PlayerStylePage(self._settings)
        self.player_style_page.setObjectName("player_style_page")
        self.lyric_page = LyricPage(self._settings)
        self.lyric_page.setObjectName("lyric_page")
        self.other_page = OtherPage(self._settings)
        self.other_page.setObjectName("other_page")

    def _init_navigation(self):
        self.addSubInterface(
            self.basic_page, FluentIcon.HOME, "基础",
            position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.file_page, FluentIcon.DOCUMENT, "文件",
            position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.player_style_page, FluentIcon.PALETTE, "播放器",
            position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.lyric_page, FluentIcon.MUSIC, "歌词",
            position=NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.other_page, FluentIcon.INFO, "其他",
            position=NavigationItemPosition.BOTTOM,
        )

    # ===================== 播放逻辑 =====================

    def _on_play(self):
        ustx_path = self._settings.ustx_path.strip()
        logger.info(f"Play 按钮点击，UST路径: {ustx_path}")

        if not ustx_path or not os.path.exists(ustx_path):
            logger.warning(f"UST 文件无效: {ustx_path}")
            InfoBar.error(
                "ERcode001", "请选择有效的UST文件！",
                5000, parent=self, position=InfoBarPosition.TOP_RIGHT,
            )
            return

        try:
            logger.info(f"开始解析 UST，编码={self._settings.encoding}")
            core_ust_info = ur.get_ust_info(ustx_path, self._settings.encoding)
            logger.info(
                f"UST 解析完成 — 版本={core_ust_info['version']}, "
                f"BPM={core_ust_info['tempo']}, "
                f"音符数={len(core_ust_info['notes'])}"
            )

            ust_info = self._settings.build_ust_info(core_ust_info)

            msg = MessageBox("WaitingForUser",
                             "按下确认后将启动播放器，鼠标单击后按ESC键退出全屏", self)
            if msg.exec():
                self._launch_player(ust_info)
            else:
                self._launch_player(ust_info)

        except UnicodeDecodeError:
            logger.exception("UST 编码错误")
            InfoBar.error(
                "ERcode004", "解析UST文件失败：使用了错误的编码，请切换编码后重试",
                5000, parent=self, position=InfoBarPosition.TOP_RIGHT,
            )
        except Exception as e:
            logger.exception("播放准备失败")
            InfoBar.error(
                "ERcode999", f"播放准备失败：{e}",
                5000, parent=self, position=InfoBarPosition.TOP_RIGHT,
            )

    def _launch_player(self, ust_info: dict):
        """启动播放器并保持引用。"""
        sc = ust_info["show_config"]
        logger.info(
            f"正在启动播放器 — curve_show={sc['curve_show']}, "
            f"bpm={sc['bpm']}, lyric={sc['lyric']}, "
            f"fullscreen={ust_info['player_style']['fullscreen']}"
        )
        try:
            self._player_window = display(ust_info)
            logger.info("播放器窗口已显示")
        except Exception:
            logger.exception("播放器启动失败")
            raise

    # ===================== 拖拽 uplr 加载 =====================

    def _load_dropped_uplr(self):
        """处理拖拽到 exe 上的 .uplr 文件（从命令行参数获取）。"""
        if len(sys.argv) <= 1:
            return

        dropped = sys.argv[1].strip()
        if not (dropped and os.path.exists(dropped) and dropped.lower().endswith(".uplr")):
            return

        try:
            self._settings.import_uplr(dropped)
            self._settings.last_open_dir = os.path.dirname(dropped)
            self._settings.write_settings()

            for page in [self.basic_page, self.file_page, self.player_style_page,
                         self.lyric_page, self.other_page]:
                page.sync_all_from_settings()

            InfoBar.success(
                "成功", f"已成功打开并加载工程：\n{dropped}",
                3000, parent=self, position=InfoBarPosition.TOP_RIGHT,
            )
        except Exception as e:
            InfoBar.error(
                "ERcode006", f"加载工程文件失败：\n{e}",
                5000, parent=self, position=InfoBarPosition.TOP_RIGHT,
            )

    # ===================== 导航切换时同步页面 =====================

    def switchTo(self, interface):
        """覆写父类方法，切换后同步页面数据。"""
        super().switchTo(interface)
        if hasattr(interface, "sync_all_from_settings"):
            interface.sync_all_from_settings()


# ===================== 程序入口 =====================

def main():
    logger.info("=" * 50)
    logger.info("ustPlayer 启动")
    logger.info(f"Python: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    try:
        from PySide6.QtCore import qVersion
        logger.info(f"Qt 版本: {qVersion()}")
    except Exception:
        pass

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("ustPlayer")

    logger.info("正在创建主窗口...")
    window = MainWindow()
    window.show()
    logger.info("主窗口已显示")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
