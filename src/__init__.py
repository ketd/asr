"""
预制件模块导出

这个文件定义了预制件对外暴露的函数列表。
"""

from .main import greet, echo, add_numbers, process_text_file, fetch_weather

__all__ = [
    "greet",
    "echo",
    "add_numbers",
    "process_text_file",
    "fetch_weather",
]
