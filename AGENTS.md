# AtHand — 全局快捷键 AI 助手

**Generated:** 2026-04-30  
**Commit:** c04a7e5  
**Branch:** main

## 项目概览

AtHand 是一个跨平台的全局快捷键唤起 AI 助手，灵感来自 macOS Spotlight。用户双击 Shift 即可唤起浮动搜索栏，快速向大模型提问并获得流式回答。

## 技术栈

| 组件 | 选型 | 说明 |
|---|---|---|
| 语言 | Python 3.11+ | |
| UI 框架 | PySide6 ≥6.6 | 无边框窗口、透明背景、毛玻璃效果 |
| 全局热键 | pynput ≥1.7.4 | 双击 Shift 检测，macOS 需辅助功能权限 |
| 系统托盘 | QSystemTrayIcon | 自动检测暗色/亮色模式切换图标 |
| LLM 调用 | openai ≥1.0 | OpenAI 兼容端点，流式传输，多轮对话 |
| Markdown | Python-Markdown + KaTeX | LaTeX 公式渲染 |
| 配置 | JSON | `~/.athand/config.json` |
| 打包 | PyInstaller ≥6.0 | macOS .app / Windows .exe / Linux AppImage |

## 项目结构

```
AtHand/
├── src/
│   ├── main.py                # 入口：初始化 QApplication、热键、托盘、窗口
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── spotlight.py       # 主浮动窗口（搜索栏 + 回答面板）
│   │   ├── answer_panel.py    # 回答区域（QWebEngineView + KaTeX 流式渲染）
│   │   ├── settings_dialog.py # 设置对话框（API Key/模型/端点/快捷键）
│   │   ├── markdown_renderer.py  # Markdown → HTML 转换（保护 LaTeX 公式）
│   │   └── styles.py          # QSS 样式常量（暗色毛玻璃主题）
│   ├── core/
│   │   ├── __init__.py
│   │   ├── hotkey.py           # pynput 双击 Shift 检测 + 回调
│   │   ├── llm.py              # OpenAI SDK 流式调用 + 消息历史管理
│   │   ├── config.py           # 配置读写、默认值
│   │   └── tray.py             # 系统托盘图标 + 菜单（动态生成图标）
│   └── resources/
│       ├── icon.svg            # 暗色图标源文件
│       ├── icon.png            # 暗色图标
│       ├── icon-light.svg      # 亮色图标源文件
│       └── icon-light.png      # 亮色图标
├── configs/
│   └── default.json            # 默认配置模板
├── requirements.txt
├── build.spec                  # PyInstaller 打包配置
└── AGENTS.md
```

## 核心交互流程

```
双击 Shift → pynput 检测 → 切换 spotlight 窗口可见性
    → 用户输入问题 → Enter 提交
    → QThread 调用 openai SDK 流式 API
    → 信号槽逐 chunk 更新 answer_panel（Markdown + KaTeX 渲染）
    → Esc 清空/隐藏（关闭窗口后清空会话历史）
```

## 配置格式 (`~/.athand/config.json`)

```json
{
  "api_key": "",
  "api_base": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "max_tokens": 4096,
  "temperature": 0.7,
  "hotkey": "double_shift",
  "theme": "dark"
}
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| 修改快捷键逻辑 | `src/core/hotkey.py` | HotkeyManager 类，双击检测间隔 300ms |
| 修改 UI 样式 | `src/ui/styles.py` | COLORS 字典 + QSS 样式表 |
| 修改 LLM 调用 | `src/core/llm.py` | LLMWorker(QThread) + ChatSession |
| 修改窗口行为 | `src/ui/spotlight.py` | SpotlightWindow 类，尺寸/定位/显隐 |
| 修改回答渲染 | `src/ui/answer_panel.py` | QWebEngineView + KaTeX CDN |
| 修改设置界面 | `src/ui/settings_dialog.py` | ConnectionTestWorker 测试连接 |
| 修改托盘图标 | `src/core/tray.py` | 自动生成，优先加载 resources/icon.* |
| 修改配置字段 | `src/core/config.py` + `configs/default.json` | 两处同步 |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| SpotlightWindow | Class | src/ui/spotlight.py | 主窗口，搜索+回答态切换 |
| HotkeyManager | Class | src/core/hotkey.py | 全局热键，双击 Shift 检测 |
| ChatSession | Class | src/core/llm.py | 多轮对话管理 |
| LLMWorker | Class | src/core/llm.py | QThread 流式请求 |
| AnswerPanel | Class | src/ui/answer_panel.py | WebEngine 渲染面板 |
| SettingsDialog | Class | src/ui/settings_dialog.py | 设置对话框 |
| SystemTray | Class | src/core/tray.py | 托盘图标+菜单 |
| render_markdown | Function | src/ui/markdown_renderer.py | Markdown+LaTeX→HTML |
| acquire_lock | Function | src/main.py | 单实例锁（Win/macOS/Linux） |

## CONVENTIONS

- **注释**: 代码注释使用中文
- **信号命名**: `chunk_received`, `response_finished`, `error_occurred`（过去分词表事件）
- **线程安全**: LLM 请求必须在 QThread 中，UI 更新通过 Signal 回传
- **配置访问**: 统一通过 `core.config.load_config()` / `save_config()`
- **热键暂停**: 设置对话框打开时调用 `hotkey.pause()`，关闭后 `resume()`
- **资源加载**: 图标优先查找文件，不存在则动态生成

## UI 设计

- **搜索态**: 640×48px 居中浮动搜索栏，暗色半透明 + 毛玻璃
- **回答态**: 展开至 ~640×450px，下方显示 Markdown 流式回答
- **视觉效果**:
  - macOS: NSVisualEffectView 毛玻璃
  - Windows 10+: Acrylic 毛玻璃
  - Linux: 半透明深色背景 fallback
- **交互**:
  - Enter 发送问题
  - Esc 关闭窗口（清空会话）
  - 多轮对话（会话内保留上下文）

## 设置界面

- API Base URL 输入框（默认 OpenAI，支持任意兼容端点）
- API Key 输入框（密码模式 + 显示/隐藏）
- Model 输入框（预设下拉 + 自定义）
- Temperature 滑块
- Max Tokens 输入
- 连接测试按钮
- 保存/取消

## 跨平台注意点

| 平台 | 热键权限 | 毛玻璃 | 打包 |
|---|---|---|---|
| macOS | 需辅助功能权限，首次运行引导 | NSVisualEffectView | .app bundle |
| Windows | 无额外权限 | Win10+ Acrylic / Win11 Mica | .exe 单文件 |
| Linux | 无额外权限 | 半透明 fallback | AppImage |

## COMMANDS

```bash
# 安装依赖
conda run -n AGENT pip install -r requirements.txt

# 启动开发
conda run -n AGENT python run.py

# 打包
conda run -n AGENT pip install pyinstaller
conda run -n AGENT pyinstaller build.spec
```

## 开发规范

- 使用 conda 环境 AGENT 运行 Python: `conda run -n AGENT python ...`
- 安装依赖: `conda run -n AGENT pip install ...`
- 代码注释默认使用中文
- 运行前执行 lint/typecheck（如有配置）
- 不要自行 git commit，除非用户明确要求