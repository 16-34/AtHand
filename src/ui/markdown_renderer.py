"""Markdown + LaTeX 渲染：将 Markdown 文本转为带 KaTeX 的 HTML"""

import re
import markdown as _md


def render_markdown(text: str) -> str:
    """将 Markdown 文本（含 LaTeX 公式）转为 HTML

    处理流程：
    1. 提取 $...$ 和 $$...$$ 公式，替换为占位符（防止 Markdown 引擎破坏公式）
    2. 用 Python-Markdown 转为 HTML
    3. 还原公式占位符，让 KaTeX 在浏览器端渲染
    """
    math_exprs: list[str] = []

    def _save_display(match):
        idx = len(math_exprs)
        math_exprs.append(match.group(0))
        return f"\nMATHD{idx}END\n"

    def _save_inline(match):
        idx = len(math_exprs)
        math_exprs.append(match.group(0))
        return f"MATHI{idx}END"

    # 先保护 $$...$$（行间公式），再保护 $...$（行内公式）
    text = re.sub(r"\$\$([\s\S]+?)\$\$", _save_display, text)
    text = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]+?)\$(?!\$)", _save_inline, text)

    html = _md.markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"],
    )

    # 还原公式：显示公式可能被 <p> 包裹，需要拆出来
    for idx, expr in enumerate(math_exprs):
        # 行间公式：移除 <p> 包裹
        wrapped_display = f"<p>\nMATHD{idx}END\n</p>"
        if wrapped_display in html:
            html = html.replace(wrapped_display, f"\n{expr}\n")
        # 行内公式：直接替换
        html = html.replace(f"MATHI{idx}END", expr)
        html = html.replace(f"MATHD{idx}END", expr)

    return html