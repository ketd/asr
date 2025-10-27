"""
预制件核心逻辑模块 - ASR 语音转文字服务

这个预制件封装了 ASR (Automatic Speech Recognition) 服务。
将音频文件（wav/mp3）转换为文字。

📁 文件路径约定：
- 输入文件：data/inputs/<音频文件>
- 一次只处理一个音频文件

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


# 固定路径常量
DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")

# ASR 服务配置
ASR_API_URL = os.environ.get("ASR_API_URL", "http://192.168.1.218:50000/api/v1/asr")


def audio_to_text(lang: str = "auto") -> dict:
    """
    将音频文件转换为文字（ASR - 自动语音识别）

    此函数调用 ASR 服务，将输入的音频文件转换为文本。
    支持多种语言和音频格式（wav/mp3，推荐 16KHz 采样率）。
    一次只处理一个音频文件。

    📁 v3.0 文件约定：
    - 输入：自动扫描 data/inputs/ 目录，处理第一个音频文件
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

    Returns:
        包含转录结果的字典，格式：
        成功时：
        {
            "text": "转录的文本内容",
            "filename": "audio.wav",
            "language": "zh",
            "raw_text": "原始文本（包含标记）",
            "clean_text": "清理后的文本"
        }

        失败时：
        {
            "error": {
                "message": "错误信息",
                "code": "ERROR_CODE"
            }
        }

    Examples:
        >>> # 自动检测语言
        >>> audio_to_text()
        {"text": "...", "filename": "test.wav", "language": "auto"}

        >>> # 指定中文
        >>> audio_to_text(lang="zh")
        {"text": "...", "filename": "test.wav", "language": "zh"}
    """
    try:
        # 1. 验证语言参数
        valid_languages = ["auto", "zh", "en", "yue", "ja", "ko", "nospeech"]
        if lang not in valid_languages:
            return {
                "error": {
                    "message": f"不支持的语言: {lang}。支持的语言: {', '.join(valid_languages)}",
                    "code": "INVALID_LANGUAGE"
                }
            }

        # 2. 扫描输入目录，获取第一个音频文件
        if not DATA_INPUTS.exists():
            return {
                "error": {
                    "message": "输入目录不存在",
                    "code": "NO_INPUT_DIR"
                }
            }

        # 支持的音频文件扩展名
        audio_extensions = {".wav", ".mp3", ".WAV", ".MP3"}
        audio_files = [
            f for f in DATA_INPUTS.iterdir()
            if f.is_file() and f.suffix in audio_extensions
        ]

        if not audio_files:
            return {
                "error": {
                    "message": "未找到音频文件（支持 .wav 和 .mp3 格式）",
                    "code": "NO_AUDIO_FILES"
                }
            }

        # 只处理第一个文件
        audio_file = audio_files[0]
        print(f"[ASR] Processing file: {audio_file.name}")

        # 3. 准备文件上传
        file_handle = None
        try:
            file_handle = open(audio_file, 'rb')
            files = [('files', (audio_file.name, file_handle, 'audio/wav'))]

            # 4. 准备表单数据
            data = {"lang": lang}

            # 5. 调用 ASR API
            response = requests.post(
                ASR_API_URL,
                files=files,
                data=data,
                timeout=300  # 5分钟超时（处理较长音频）
            )

            # 检查响应状态
            if response.status_code != 200:
                return {
                    "error": {
                        "message": f"ASR 服务返回错误: HTTP {response.status_code} - {response.text}",
                        "code": "ASR_API_ERROR"
                    }
                }

            # 解析响应
            result_data = response.json()

            # 6. 格式化返回结果
            # ASR 服务返回格式: {"result": [{"key": "filename", "text": "...", ...}]}
            if isinstance(result_data, dict) and "result" in result_data:
                results = result_data["result"]
                if results and len(results) > 0:
                    first_result = results[0]
                    return {
                        "text": first_result.get("clean_text") or first_result.get("text", ""),
                        "filename": audio_file.name,
                        "language": lang,
                        "raw_text": first_result.get("raw_text", ""),
                        "clean_text": first_result.get("clean_text", "")
                    }

            # 如果格式不符合预期，返回原始数据
            return {
                "text": str(result_data),
                "filename": audio_file.name,
                "language": lang
            }

        except requests.exceptions.Timeout:
            return {
                "error": {
                    "message": "ASR 服务请求超时（5分钟）",
                    "code": "TIMEOUT"
                }
            }

        except requests.exceptions.ConnectionError:
            return {
                "error": {
                    "message": f"无法连接到 ASR 服务: {ASR_API_URL}",
                    "code": "CONNECTION_ERROR"
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                "error": {
                    "message": f"请求 ASR 服务时发生错误: {str(e)}",
                    "code": "REQUEST_ERROR"
                }
            }

        except ValueError as e:
            return {
                "error": {
                    "message": f"解析 ASR 响应失败: {str(e)}",
                    "code": "PARSE_ERROR"
                }
            }

        except Exception as e:
            return {
                "error": {
                    "message": f"打开或处理音频文件失败: {str(e)}",
                    "code": "FILE_ERROR"
                }
            }

        finally:
            # 确保关闭文件
            if file_handle:
                file_handle.close()

    except Exception as e:
        return {
            "error": {
                "message": str(e),
                "code": "UNEXPECTED_ERROR"
            }
        }
