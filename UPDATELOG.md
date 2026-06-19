# 更新日志

>[!TIP]
>本文档使用AI编写

>[!CAUTION]
>此版本包含破坏性修改，可能不是很稳定，请三思而后行！

## v26f19 (2026-06-19) — PySide6 Fluent 重制版

### 框架迁移：tkinter → PySide6 + Fluent Design

全面重写 UI 框架，从 tkinter 迁移至 PySide6，采用 PySide6-Fluent-Widgets 组件库实现现代 Fluent Design 风格界面。

### 项目结构

```
ustPlayer/
├── main.py                     # 入口，QApplication + MSFluentWindow
├── requirements.txt            # 依赖声明
├── core/
│   ├── settings_manager.py     # 配置管理器（28个信号驱动属性）
│   ├── ustreader.py            # UST 解析器（优化版）
│   ├── ustplayer.py            # 全屏播放器（QPainter 渲染）
│   └── log.py                  # 日志系统（文件+控制台双输出）
├── ui/
│   ├── basic_page.py           # 基础 — 项目信息、显示选项、Play
│   ├── file_page.py            # 文件 — UST选择、编码、预览
│   ├── player_style_page.py    # 播放器 — 5色选择、静默/结束显示
│   ├── lyric_page.py           # 歌词 — LRC导入、显示开关
│   └── other_page.py           # 其他 — 版权、工具、协议
├── Terms.txt / ERcode.txt      # 协议与错误码
└── icon.ico / icon.png         # 图标
```

### 新增功能

- **侧边导航栏**：MSFluentWindow + NavigationInterface，替代原有自绘标签页
- **日志系统**：`core/log.py` 提供文件（DEBUG）+ 控制台（INFO）双输出，记录启动信息、播放参数、异常堆栈
- **信号驱动配置**：SettingsManager 的 28 个属性均通过 Qt Signal 通知变更，支持反应式数据绑定
- **工程文件完整支持**：`.uplr` 导入/导出涵盖全部 5 个配置段
- **非阻塞提示**：InfoBar 替代 messagebox，不阻塞操作

### 优化

- **UST 解析器**：`with` 语句、类型注解、异常处理、独立解析函数
- **文本渲染**：`QFontMetrics.horizontalAdvance() + height()` 替代 `boundingRect()`，20% padding 防止 CJK 字形裁切
- **全屏播放器**：
  - QPainter 硬件加速渲染，原生抗锯齿
  - 窗口标志在 show 前统一设置，消除全屏边角漏出
  - resizeEvent 实时更新尺寸，避免坐标偏移
  - QTimer 5ms 高精度刷新

### 组件对照

| 原 tkinter | 新 PySide6 / qfluentwidgets |
|-----------|----------------------------|
| `tk.Tk()` | `QApplication` |
| 自绘标签页 | `MSFluentWindow` + 侧边导航 |
| `ttk.Entry` | `LineEdit` |
| `ttk.Button` | `PrimaryPushButton` / `PushButton` |
| `tk.Checkbutton` | `CheckBox` |
| `ttk.Combobox` | `ComboBox` |
| `scrolledtext.ScrolledText` | `TextEdit` (只读) |
| `messagebox` | `InfoBar` / `MessageBox` |
| `filedialog` | `QFileDialog` |
| `colorchooser` | `ColorPickerButton`（Fluent 内置取色器）|
| `tk.Canvas` | `QPainter` (paintEvent) |

### 后续修复 (v26f19)

- **颜色选择器升级**：`QColorDialog` → `ColorPickerButton`（qfluentwidgets 内置 Fluent 风格取色器）
  - 点击即弹出 Fluent Design 取色面板，无需调用系统对话框
  - LineEdit ↔ ColorPickerButton ↔ Settings 三向同步，双向更新互不干扰（`blockSignals` 防循环）
- **文本裁切修复**：`boundingRect()` → `horizontalAdvance() + height()` + 20% padding，解决 CJK 字形被截问题
- **全屏边角修复**：窗口标志在 `show()` 前统一设置 `FramelessWindowHint | WindowStaysOnTopHint`，消除边角漏出
- **音高线诊断**：播放器启动日志报告 `含PitchBend的音符=N`，音符切换时记录绘制决策

### 依赖

```
PySide6 >= 6.5.0
PySide6-Fluent-Widgets[full] >= 1.5.0
```
