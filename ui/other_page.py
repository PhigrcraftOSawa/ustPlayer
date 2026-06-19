# other_page.py — "其他" 导航页
"""版权信息、外部工具、使用协议入口。"""

import os
import subprocess
import webbrowser
from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from qfluentwidgets import (
    PushButton, BodyLabel, StrongBodyLabel, HorizontalSeparator,
    InfoBar, InfoBarPosition,
)

from core.settings_manager import SettingsManager


class OtherPage(QWidget):
    """其他标签页 — 关于软件 / 工具 / 协议。"""

    def __init__(self, settings: SettingsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._s = settings
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        layout.addWidget(StrongBodyLabel("/ 关于软件"))

        # 版权信息（可点击）
        copyright_lbl = BodyLabel("ustPlayer - v26f19 (c) 2026 SYEternal_R & 灰棱HiRenG")
        copyright_lbl.setStyleSheet("color: #0066CC;")
        copyright_lbl.setCursor(Qt.PointingHandCursor)
        copyright_lbl.mousePressEvent = lambda e: self._open_url(
            "https://space.bilibili.com/661930756"
        )
        layout.addWidget(copyright_lbl)

        layout.addWidget(HorizontalSeparator())

        # 外部工具与纠错
        layout.addWidget(StrongBodyLabel("/ 外部工具与纠错"))

        tool_row = QHBoxLayout()
        tool_row.setSpacing(12)

        uf_btn = PushButton("UtaFormatix")
        uf_btn.clicked.connect(lambda: self._open_url("https://utaformatix.tk/"))
        tool_row.addWidget(uf_btn)

        er_btn = PushButton("ERcodes纠错")
        er_btn.clicked.connect(self._open_ercode)
        tool_row.addWidget(er_btn)
        tool_row.addStretch()
        layout.addLayout(tool_row)

        layout.addWidget(HorizontalSeparator())

        # 协议与许可
        layout.addWidget(StrongBodyLabel("/ 协议与许可"))

        lic_row = QHBoxLayout()
        lic_row.setSpacing(12)

        terms_btn = PushButton("使用协议")
        terms_btn.clicked.connect(self._open_terms)
        lic_row.addWidget(terms_btn)

        gh_btn = PushButton("GitHub仓库")
        gh_btn.clicked.connect(
            lambda: self._open_url("https://github.com/SYEternalR/ustPlayer")
        )
        lic_row.addWidget(gh_btn)
        lic_row.addStretch()
        layout.addLayout(lic_row)

        layout.addWidget(HorizontalSeparator())

        # 彩蛋
        easter = BodyLabel("你知道吗：alpha版本在提交至托管时曾被错误地命名为ustPlyaer。orz")
        easter.setWordWrap(True)
        layout.addWidget(easter)

        layout.addStretch()

    # ===================== 工具方法 =====================

    def _open_url(self, url: str):
        try:
            webbrowser.open(url, new=2)
        except Exception as e:
            InfoBar.error("ERcode003", f"打开网页失败：{e}", 5000,
                          parent=self.window(), position=InfoBarPosition.TOP_RIGHT)

    def _open_ercode(self):
        try:
            path = self._s.ercode_file_path
            subprocess.Popen(
                ["notepad.exe", path],
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        except Exception as e:
            InfoBar.error("ERcode008", f"打开ERcode.txt失败：{e}", 5000,
                          parent=self.window(), position=InfoBarPosition.TOP_RIGHT)

    def _open_terms(self):
        try:
            path = self._s.terms_file_path
            subprocess.Popen(
                ["notepad.exe", path],
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        except Exception as e:
            InfoBar.error("ERcode009", f"打开Terms.txt失败：{e}", 5000,
                          parent=self.window(), position=InfoBarPosition.TOP_RIGHT)

    def sync_all_from_settings(self):
        """其他页无动态配置，无需同步。"""
        pass
