#!/usr/bin/env python3
"""AtHand 启动脚本"""

import sys
import os

# 将 src 目录加入模块路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# macOS 需要 layer-backed view
if sys.platform == "darwin":
    os.environ["QT_MAC_WANTS_LAYER"] = "1"

from src.main import main

if __name__ == "__main__":
    main()