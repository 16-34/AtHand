"""配置管理模块：读写 ~/.athand/config.json，提供默认值"""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".athand"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "api_key": "",
    "api_base": "https://api.openai.com/v1",
    "model": "gpt-4o-mini",
    "max_tokens": 4096,
    "temperature": 0.7,
    "hotkey": "double_shift",
    "theme": "dark",
}


def _ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """加载配置，缺失字段用默认值填充"""
    _ensure_config_dir()
    config = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            user_config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            config.update(user_config)
        except (json.JSONDecodeError, OSError):
            pass
    return config


def save_config(config: dict):
    """保存配置到文件"""
    _ensure_config_dir()
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )