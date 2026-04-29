"""LLM 调用模块：litellm 流式调用 + 多轮对话管理"""

from PySide6.QtCore import QObject, Signal, QThread


class LLMWorker(QThread):
    """后台线程执行 LLM 流式调用"""

    chunk_received = Signal(str)  # 逐 chunk 推送
    finished = Signal(str)  # 完成时推送完整回答
    error_occurred = Signal(str)  # 错误信息

    def __init__(self, messages: list[dict], config: dict, parent=None):
        super().__init__(parent)
        self.messages = messages
        self.config = config
        self._full_response = ""

    def run(self):
        """在后台线程中执行流式调用（延迟导入 litellm 避免启动慢）"""
        try:
            import litellm
        except ImportError:
            self.error_occurred.emit("litellm 未安装，请运行 pip install litellm")
            return

        try:
            api_key = self.config.get("api_key", "")
            api_base = self.config.get("api_base", "https://api.openai.com/v1")
            model = self.config.get("model", "gpt-4o-mini")
            max_tokens = self.config.get("max_tokens", 4096)
            temperature = self.config.get("temperature", 0.7)

            if not api_key:
                self.error_occurred.emit("请先在设置中配置 API Key")
                return

            # 自定义 api_base 时需要 openai/ 前缀让 litellm 识别
            actual_model = model
            if api_base and api_base != "https://api.openai.com/v1":
                if not model.startswith("openai/"):
                    actual_model = f"openai/{model}"

            kwargs = {
                "model": actual_model,
                "messages": self.messages,
                "stream": True,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "api_key": api_key,
            }

            if api_base and api_base != "https://api.openai.com/v1":
                kwargs["api_base"] = api_base

            response = litellm.completion(**kwargs)

            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    self._full_response += delta
                    self.chunk_received.emit(delta)

            self.finished.emit(self._full_response)

        except litellm.AuthenticationError:
            self.error_occurred.emit("API Key 无效，请检查设置")
        except litellm.RateLimitError:
            self.error_occurred.emit("请求频率超限，请稍后重试")
        except litellm.ContextWindowExceededError:
            self.error_occurred.emit("上下文长度超限，请开启新会话")
        except Exception as e:
            self.error_occurred.emit(f"请求失败: {str(e)}")


class ChatSession(QObject):
    """多轮对话会话管理"""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.history: list[dict] = []  # 消息历史
        self._worker: LLMWorker | None = None

    # 向外暴露的信号（由 worker 转发）
    chunk_received = Signal(str)
    response_finished = Signal(str)
    error_occurred = Signal(str)

    def send(self, user_message: str):
        """发送用户消息并启动流式请求"""
        self.history.append({"role": "user", "content": user_message})

        self._worker = LLMWorker(list(self.history), self.config)
        self._worker.chunk_received.connect(self.chunk_received.emit)
        self._worker.error_occurred.connect(self.error_occurred.emit)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, full_response: str):
        """流式完成，将 assistant 回答加入历史"""
        self.history.append({"role": "assistant", "content": full_response})
        self.response_finished.emit(full_response)

    def clear(self):
        """清空会话历史"""
        self.history.clear()
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()
        self._worker = None

    def is_busy(self) -> bool:
        """是否正在请求中"""
        return self._worker is not None and self._worker.isRunning()

    def update_config(self, config: dict):
        """更新配置"""
        self.config = config