# AtHand

全局快捷键唤起的 AI 助手，灵感来自 macOS Spotlight。

双击 `Shift` 即可唤起浮动搜索栏，快速向大模型提问并获得流式回答。

## 功能特性

- **全局快捷键** — 双击 Shift 随时唤起，无需切换窗口
- **流式回答** — 实时 Markdown 渲染，逐字输出
- **多轮对话** — 会话内保留上下文，支持追问
- **OpenAI 兼容** — 支持任意 OpenAI 兼容端点（OpenAI / DeepSeek / 本地模型等）
- **应用内设置** — API Key、模型、温度等参数可界面配置，含连接测试
- **系统托盘** — 常驻后台，双击托盘图标也可唤起
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

## 项目结构

```
src/
├── main.py              # 入口
├── core/
│   ├── config.py        # 配置读写
│   ├── hotkey.py        # 双击 Shift 检测
│   ├── llm.py           # litellm 流式调用 + 多轮对话
│   └── tray.py          # 系统托盘
├── ui/
│   ├── spotlight.py     # 主浮动窗口
│   ├── answer_panel.py  # 流式 Markdown 回答面板
│   ├── settings_dialog.py # 设置界面
│   └── styles.py        # 暗色毛玻璃主题样式
└── resources/
    └── icon.png
```

## macOS 权限

全局快捷键需要辅助功能权限。首次运行会弹出引导提示，请在 **系统设置 > 隐私与安全 > 辅助功能** 中授权 AtHand。

## 打包

```bash
conda run -n AGENT pip install pyinstaller
conda run -n AGENT pyinstaller build.spec
```

## 技术栈

| 组件 | 选型 |
|---|---|
| UI | PySide6 |
| 全局热键 | pynput |
| 系统托盘 | pystray |
| LLM 调用 | litellm |
| 打包 | PyInstaller |