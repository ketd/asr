"""
预制件核心逻辑模块 - ASR 语音转文字服务

这个预制件封装了 ASR (Automatic Speech Recognition) 服务。
将音频文件（wav/mp3）转换为文字。

📁 文件路径约定：
- 输入文件：data/inputs/<音频文件>
- 输出文件：data/outputs/<结果文件>（如需要）

🎤 支持的音频格式：
- WAV（推荐 16KHz 采样率）
- MP3（推荐 16KHz 采样率）

🌐 支持的语言：
- auto: 自动检测
- zh: 中文（普通话）
- en: 英语
- yue: 粤语
- ja: 日语
- ko: 韩语
- nospeech: 无语音
"""

import os
import requests
from pathlib import Path
from typing import Dict, Any


# 固定路径常量
DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")

# ASR 服务配置
ASR_API_URL = os.environ.get("ASR_API_URL", "http://192.168.1.218:50000/api/v1/asr")


def audio_to_text(lang: str = "auto", keys: str = "") -> dict:
    """
    将音频文件转换为文字（ASR - 自动语音识别）

    此函数调用 ASR 服务，将输入的音频文件转换为文本。
    支持多种语言和音频格式（wav/mp3，推荐 16KHz 采样率）。

    📁 v3.0 文件约定：
    - 输入：自动扫描 data/inputs/ 目录下的所有音频文件
    - Gateway 已将用户上传的文件下载到该目录

    🎤 支持的音频格式：
    - WAV（推荐 16KHz 采样率）
    - MP3（推荐 16KHz 采样率）

    🌐 支持的语言：
    - auto: 自动检测（默认）
    - zh: 中文（普通话）
    - en: 英语
    - yue: 粤语
    - ja: 日语
    - ko: 韩语
    - nospeech: 无语音

    Args:
        lang: 音频内容的语言，默认为 "auto" 自动检测
        keys: 每个音频文件的名称，用逗号连接（可选，如果为空则使用文件名）

    Returns:
        包含转录结果的字典，格式：
        {
            "success": True/False,
            "results": [
                {
                    "filename": "audio1.wav",
                    "text": "转录的文本内容",
                    "language": "zh"
                },
                ...
            ],
            "total_files": 整数,
            "error": "错误信息（失败时）",
            "error_code": "错误代码（失败时）"
        }

    Examples:
        >>> # 自动检测语言
        >>> audio_to_text()
        {"success": True, "results": [...], "total_files": 1}

        >>> # 指定中文
        >>> audio_to_text(lang="zh")
        {"success": True, "results": [...], "total_files": 1}

        >>> # 指定文件名
        >>> audio_to_text(lang="auto", keys="recording1,recording2")
        {"success": True, "results": [...], "total_files": 2}
    """
    try:
        # 1. 验证语言参数
        valid_languages = ["auto", "zh", "en", "yue", "ja", "ko", "nospeech"]
        if lang not in valid_languages:
            return {
                "success": False,
                "error": f"不支持的语言: {lang}。支持的语言: {', '.join(valid_languages)}",
                "error_code": "INVALID_LANGUAGE"
            }

        # 2. 扫描输入目录，获取所有音频文件
        if not DATA_INPUTS.exists():
            return {
                "success": False,
                "error": "输入目录不存在",
                "error_code": "NO_INPUT_DIR"
            }

        # 支持的音频文件扩展名
        audio_extensions = {".wav", ".mp3", ".WAV", ".MP3"}
        audio_files = [
            f for f in DATA_INPUTS.iterdir()
            if f.is_file() and f.suffix in audio_extensions
        ]

        if not audio_files:
            return {
                "success": False,
                "error": "未找到音频文件（支持 .wav 和 .mp3 格式）",
                "error_code": "NO_AUDIO_FILES"
            }

        # 3. 准备文件上传
        files = []
        try:
            for audio_file in audio_files:
                files.append(
                    ('files', (audio_file.name, open(audio_file, 'rb'), 'audio/wav'))
                )
        except Exception as e:
            # 确保关闭所有已打开的文件
            for _, file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
            return {
                "success": False,
                "error": f"打开音频文件失败: {str(e)}",
                "error_code": "FILE_OPEN_ERROR"
            }

        # 4. 准备表单数据
        data = {
            "lang": lang
        }

        # 如果提供了 keys，添加到请求中
        if keys and keys.strip():
            data["keys"] = keys.strip()

        # 5. 调用 ASR API
        try:
            response = requests.post(
                ASR_API_URL,
                files=files,
                data=data,
                timeout=300  # 5分钟超时（处理较长音频）
            )

            # 关闭所有文件句柄
            for _, file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

            # 检查响应状态
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"ASR 服务返回错误: HTTP {response.status_code}",
                    "error_code": "ASR_API_ERROR",
                    "details": response.text
                }

            # 解析响应
            result_data = response.json()

            # 6. 格式化返回结果
            return {
                "success": True,
                "results": result_data,
                "total_files": len(audio_files),
                "language": lang,
                "api_url": ASR_API_URL
            }

        except requests.exceptions.Timeout:
            # 关闭文件
            for _, file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
            return {
                "success": False,
                "error": "ASR 服务请求超时（5分钟）",
                "error_code": "TIMEOUT"
            }

        except requests.exceptions.ConnectionError:
            # 关闭文件
            for _, file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
            return {
                "success": False,
                "error": f"无法连接到 ASR 服务: {ASR_API_URL}",
                "error_code": "CONNECTION_ERROR"
            }

        except requests.exceptions.RequestException as e:
            # 关闭文件
            for _, file_tuple in files:
                if len(file_tuple) > 1 and hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
            return {
                "success": False,
                "error": f"请求 ASR 服务时发生错误: {str(e)}",
                "error_code": "REQUEST_ERROR"
            }

        except ValueError as e:
            return {
                "success": False,
                "error": f"解析 ASR 响应失败: {str(e)}",
                "error_code": "PARSE_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
