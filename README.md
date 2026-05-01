# AtHand-Tauri

使用 Tauri 重构的 AtHand —— 全局快捷键 AI 助手

## 特性

- **超小包体积**: ~8MB (对比 Python 版本的 ~200MB)
- **极速启动**: 原生级性能
- **完全相同的 UI**: 暗色毛玻璃主题，像素级复刻
- **双击 Shift 唤起**: 全局热键监听
- **Markdown + KaTeX**: 公式渲染支持
- **OpenAI 兼容**: 支持任意 OpenAI 兼容端点

## 技术栈

- **后端**: Rust + Tauri
- **前端**: Vanilla JS + KaTeX + Marked
- **热键**: rdev (跨平台原生热键监听)
- **HTTP**: reqwest (流式 SSE 请求)

## 安装

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Tauri CLI
cargo install tauri-cli

# 安装 Node 依赖
npm install

# 开发模式
npm run tauri dev

# 打包
npm run tauri build
```

## 项目结构

```
AtHand-Tauri/
├── src/                    # 前端代码
│   └── main.js            # 主逻辑
├── src-tauri/             # Rust 后端
│   ├── src/
│   │   ├── main.rs        # 入口
│   │   ├── config.rs      # 配置管理
│   │   ├── hotkey.rs      # 双击 Shift 热键
│   │   └── llm.rs         # LLM API 调用
│   ├── Cargo.toml
│   └── tauri.conf.json
├── index.html
├── package.json
└── README.md
```

## 配置

配置文件位置: `~/.athand/config.json`

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

## 跨平台支持

| 平台 | 状态 | 备注 |
|------|------|------|
| macOS | ✅ | 需要辅助功能权限 |
| Windows | ✅ | 直接运行 |
| Linux | ✅ | X11/Wayland |

## 许可证

MIT
