# AtHand

全局快捷键唤起的 AI 助手，灵感来自 macOS Spotlight。

双击 `Shift` 即可唤起浮动搜索栏，快速向大模型提问并获得流式回答。

![暗色主题](src/resources/icon.svg)

## 功能特性

- **全局快捷键** — 双击 Shift 随时唤起，无需切换窗口
- **流式回答** — 实时渲染 Markdown + LaTeX 公式（KaTeX）
- **多轮对话** — 会话内保留完整上下文，支持追问
- **OpenAI 兼容** — 支持任意 OpenAI 兼容端点（OpenAI / 硅基流动 / DeepSeek / 本地模型等）
- **应用内设置** — API Key、模型、温度等参数可界面配置，含连接测试
- **系统托盘** — 常驻后台，托盘菜单可唤起 / 设置 / 退出
- **单实例运行** — 同一时间只允许一个进程
- **跨平台** — macOS / Windows / Linux

## 快速开始

### 环境要求

- Python 3.11+
- conda 环境（推荐）

### 安装依赖

```bash
conda run -n AGENT pip install -r requirements.txt
```

### 启动

```bash
conda run -n AGENT python run.py
```

首次启动会自动打开设置界面，填写 API Key 和端点后即可使用。

## 使用方式

| 操作 | 说明 |
|---|---|
| **双击 Shift** | 唤起 / 隐藏搜索栏 |
| **Enter** | 发送问题 |
| **Esc** | 关闭窗口（清空会话） |
| **托盘图标** | 右键菜单：显示 / 设置 / 退出 |

## 界面预览

- **搜索态**：640×52 居中浮动搜索栏，简约黑白主题
- **回答态**：展开至 640×450，多轮对话历史 + Markdown + LaTeX 公式渲染
- **设置页**：分组式布局，连接测试，密码框支持显示切换

## 配置

配置文件位于 `~/.athand/config.json`：

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

### 推荐端点

| 服务商 | api_base | 模型示例 |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | gpt-4o-mini, gpt-4o |
| 硅基流动 | `https://api.siliconflow.cn/v1` | Qwen/Qwen2.5-72B-Instruct |
| DeepSeek | `https://api.deepseek.com/v1` | deepseek-chat |

> 设置界面中的模型下拉框已预置常用模型，也可手动输入任意模型名称。

## 项目结构

```
src/
├── main.py                # 入口：QApplication、热键、托盘、单实例锁
├── core/
│   ├── config.py          # 配置读写
│   ├── hotkey.py           # pynput 双击 Shift 检测（可暂停）
│   ├── llm.py              # OpenAI SDK 流式调用 + 多轮对话
│   └── tray.py             # 系统托盘（自动检测暗色/亮色模式）
├── ui/
│   ├── spotlight.py        # 主浮动窗口
│   ├── answer_panel.py     # QWebEngineView + KaTeX 回答面板
│   ├── markdown_renderer.py # Markdown → HTML 转换（保护 LaTeX）
│   ├── settings_dialog.py  # 设置界面
│   └── styles.py           # 简约黑白主题 QSS
└── resources/
    ├── icon.svg            # 暗色图标源文件
    ├── icon.png             # 暗色图标
    ├── icon-light.svg       # 亮色图标源文件
    └── icon-light.png        # 亮色图标
```

## macOS 权限

全局快捷键需要辅助功能权限。首次运行会弹出引导提示，请在 **系统设置 > 隐私与安全 > 辅助功能** 中授权 AtHand。

## 打包

```bash
conda run -n AGENT pip install pyinstaller
conda run -n AGENT pyinstaller build.spec
```

## 技术栈

| 组件 | 选型 | 说明 |
|---|---|---|
| UI 框架 | PySide6 | 无边框窗口、透明背景、QWebEngineView |
| 全局热键 | pynput | 双击 Shift 检测，设置对话框时自动暂停 |
| 系统托盘 | QSystemTrayIcon | 自动检测暗色/亮色模式切换图标 |
| LLM 调用 | openai SDK | 任意 OpenAI 兼容端点，流式传输 |
| Markdown | Python-Markdown + KaTeX | LaTeX 公式渲染 |
| 配置 | JSON | `~/.athand/config.json` |
| 打包 | PyInstaller | macOS .app / Windows .exe / Linux AppImage |