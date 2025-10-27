"""
ASR 预制件模块导出

这个文件定义了 ASR 预制件对外暴露的函数列表。
"""

from .main import audio_to_text

__all__ = [
    "audio_to_text",
]
