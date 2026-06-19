# basic_page.py — "基础" 导航页
"""项目信息、显示选项和播放控制。"""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QFileDialog,
)
from PySide6.QtCore import Qt

from qfluentwidgets import (
    LineEdit, PushButton, PrimaryPushButton, CheckBox,
    BodyLabel, StrongBodyLabel, HorizontalSeparator,
    InfoBar, InfoBarPosition,
)

from core.settings_manager import SettingsManager


class BasicPage(QWidget):
    """基础标签页 — 项目信息 + 显示选项 + Play 按钮。"""

    def __init__(self, settings: SettingsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._s = settings
        self._play_callback: Optional[callable] = None
        self._setup_ui()
        self._connect_signals()

    def set_play_callback(self, callback: callable):
        """由 main.py 注入播放回调。"""
        self._play_callback = callback

    # ===================== UI 构建 =====================

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # ---- 顶部按钮 ----
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.import_btn = PushButton("导入项目")
        self.export_btn = PushButton("保存项目")
        btn_row.addWidget(self.import_btn)
        btn_row.addWidget(self.export_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addWidget(HorizontalSeparator())

        # ---- 关于项目 ----
        layout.addWidget(StrongBodyLabel("/ 关于项目"))

        self._add_field(layout, "项目名：", "project_name")
        self._add_field(layout, "曲名&曲师：", "song_name")
        self._add_field(layout, "MIDI作者：", "song_author")
        self._add_field(layout, "调音师：", "ust_author")

        layout.addWidget(HorizontalSeparator())

        # ---- 基础信息 ----
        layout.addWidget(StrongBodyLabel("/ 基础信息"))

        # 复选框行
        cb_grid = QVBoxLayout()
        cb_grid.setSpacing(8)

        row1 = QHBoxLayout()
        self.cb_bpm = CheckBox("显示BPM")
        self.cb_play_time = CheckBox("显示播放时间")
        row1.addWidget(self.cb_bpm)
        row1.addWidget(self.cb_play_time)
        row1.addStretch()
        cb_grid.addLayout(row1)

        row2 = QHBoxLayout()
        self.cb_song_name = CheckBox("显示曲目信息")
        self.cb_song_author = CheckBox("显示MIDI作者")
        row2.addWidget(self.cb_song_name)
        row2.addWidget(self.cb_song_author)
        row2.addStretch()
        cb_grid.addLayout(row2)

        row3 = QHBoxLayout()
        self.cb_ust_author = CheckBox("显示调音师")
        row3.addWidget(self.cb_ust_author)
        row3.addStretch()
        cb_grid.addLayout(row3)

        layout.addLayout(cb_grid)

        layout.addStretch()

        # ---- Play 按钮 ----
        self.play_btn = PrimaryPushButton("播放 Play")
        self.play_btn.setMinimumHeight(40)
        layout.addWidget(self.play_btn)

    def _add_field(self, parent_layout: QVBoxLayout, label: str, attr: str):
        """添加标签 + 输入框行。"""
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = BodyLabel(label)
        lbl.setMinimumWidth(90)
        row.addWidget(lbl)

        edit = LineEdit()
        edit.setPlaceholderText(f"请输入{label.strip('：')}")
        row.addWidget(edit, 1)

        # 保存引用以便双向绑定
        setattr(self, f"edit_{attr}", edit)

        parent_layout.addLayout(row)

    # ===================== 信号绑定 =====================

    def _connect_signals(self):
        s = self._s

        # 初始值 → UI
        self.edit_project_name.setText(s.project_name)
        self.edit_song_name.setText(s.song_name)
        self.edit_song_author.setText(s.song_author)
        self.edit_ust_author.setText(s.ust_author)
        self.cb_bpm.setChecked(s.show_bpm)
        self.cb_play_time.setChecked(s.show_play_time)
        self.cb_song_name.setChecked(s.show_song_name)
        self.cb_song_author.setChecked(s.show_song_author)
        self.cb_ust_author.setChecked(s.show_ust_author)

        # UI → settings
        self.edit_project_name.textChanged.connect(lambda v: setattr(s, "project_name", v))
        self.edit_song_name.textChanged.connect(lambda v: setattr(s, "song_name", v))
        self.edit_song_author.textChanged.connect(lambda v: setattr(s, "song_author", v))
        self.edit_ust_author.textChanged.connect(lambda v: setattr(s, "ust_author", v))
        self.cb_bpm.checkStateChanged.connect(lambda v: setattr(s, "show_bpm", v == Qt.Checked))
        self.cb_play_time.checkStateChanged.connect(lambda v: setattr(s, "show_play_time", v == Qt.Checked))
        self.cb_song_name.checkStateChanged.connect(lambda v: setattr(s, "show_song_name", v == Qt.Checked))
        self.cb_song_author.checkStateChanged.connect(lambda v: setattr(s, "show_song_author", v == Qt.Checked))
        self.cb_ust_author.checkStateChanged.connect(lambda v: setattr(s, "show_ust_author", v == Qt.Checked))

        # 按钮
        self.import_btn.clicked.connect(self._on_import)
        self.export_btn.clicked.connect(self._on_export)
        self.play_btn.clicked.connect(self._on_play)

    # ===================== 业务逻辑 =====================

    def _on_import(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开工程文件",
            self._s.last_open_dir,
            "ustPlayer工程文件 (*.uplr);;所有文件 (*.*)",
        )
        if not file_path:
            return
        try:
            self._s.import_uplr(file_path)
            self._sync_ui_from_settings()
            self._s.last_open_dir = os.path.dirname(file_path)
            self._s.write_settings()
            InfoBar.success("成功", f"已加载工程：{file_path}", 3000,
                            parent=self.window(), position=InfoBarPosition.TOP_RIGHT)
        except Exception as e:
            InfoBar.error("ERcode007", f"加载文件失败：{e}", 5000,
                          parent=self.window(), position=InfoBarPosition.TOP_RIGHT)

    def _on_export(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出你的工程文件",
            os.path.join(self._s.last_export_dir, self._s.project_name or "未命名"),
            "ustPlayer工程文件 (*.uplr);;所有文件 (*.*)",
        )
        if not file_path:
            return
        try:
            self._s.export_uplr(file_path)
            self._s.last_export_dir = os.path.dirname(file_path)
            self._s.write_settings()
            InfoBar.success("成功", f"工程已导出到：{file_path}", 3000,
                            parent=self.window(), position=InfoBarPosition.TOP_RIGHT)
        except Exception as e:
            InfoBar.error("ERcode006", f"导出失败：{e}", 5000,
                          parent=self.window(), position=InfoBarPosition.TOP_RIGHT)

    def _on_play(self):
        if self._play_callback:
            self._play_callback()

    def _sync_ui_from_settings(self):
        """导入 .uplr 后，将 settings 的值同步回 UI。"""
        s = self._s
        self.edit_project_name.setText(s.project_name)
        self.edit_song_name.setText(s.song_name)
        self.edit_song_author.setText(s.song_author)
        self.edit_ust_author.setText(s.ust_author)
        self.cb_bpm.setChecked(s.show_bpm)
        self.cb_play_time.setChecked(s.show_play_time)
        self.cb_song_name.setChecked(s.show_song_name)
        self.cb_song_author.setChecked(s.show_song_author)
        self.cb_ust_author.setChecked(s.show_ust_author)

    def sync_all_from_settings(self):
        """供 main.py 调用，导入 uplr 后刷新所有页面。"""
        self._sync_ui_from_settings()
