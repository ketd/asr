"""
ASR 预制件核心函数测试

测试语音识别功能，确保函数按预期工作。
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import os
from unittest.mock import Mock, patch
from src.main import audio_to_text


class TestASRFunction:
    """测试 ASR 音频转文字功能"""

    @pytest.fixture
    def workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)

        # 创建目录结构（v3.0: 文件组在子目录中）
        inputs_dir = workspace_path / "data" / "inputs" / "input"
        inputs_dir.mkdir(parents=True)

        # 切换到工作空间
        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        yield workspace_path

        # 清理
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def workspace_with_audio(self, workspace):
        """创建包含音频文件的工作空间"""
        inputs_dir = workspace / "data" / "inputs" / "input"

        # 创建模拟音频文件（空文件，仅用于测试文件扫描）
        audio_file = inputs_dir / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        return workspace

    def test_audio_to_text_invalid_language(self, workspace_with_audio):
        """测试无效的语言参数"""
        result = audio_to_text(lang="invalid_lang")

        assert "error" in result
        assert result["error"]["code"] == "INVALID_LANGUAGE"
        assert "不支持的语言" in result["error"]["message"]

    def test_audio_to_text_no_input_dir(self):
        """测试输入目录不存在"""
        # 在一个不存在 data/inputs 的目录中运行
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            result = audio_to_text()

            os.chdir(original_cwd)

            assert "error" in result
            assert result["error"]["code"] == "NO_INPUT_DIR"

    def test_audio_to_text_no_audio_files(self, workspace):
        """测试没有音频文件"""
        result = audio_to_text()

        assert "error" in result
        assert result["error"]["code"] == "NO_AUDIO_FILES"
        assert "未找到音频文件" in result["error"]["message"]

    @patch('src.main.requests.post')
    def test_audio_to_text_success(self, mock_post, workspace_with_audio):
        """测试成功转录（模拟 API 响应）"""
        # 模拟 ASR API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {
                    "key": "test.wav",
                    "text": "这是一段测试音频",
                    "clean_text": "这是一段测试音频",
                    "raw_text": "<|zh|>这是一段测试音频"
                }
            ]
        }
        mock_post.return_value = mock_response

        result = audio_to_text(lang="zh")

        assert "error" not in result
        assert "text" in result
        assert result["text"] == "这是一段测试音频"
        assert result["filename"] == "test.wav"
        assert result["language"] == "zh"

    @patch('src.main.requests.post')
    def test_audio_to_text_api_error(self, mock_post, workspace_with_audio):
        """测试 API 返回错误状态码"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = audio_to_text()

        assert "error" in result
        assert result["error"]["code"] == "ASR_API_ERROR"
        assert "HTTP 500" in result["error"]["message"]

    @patch('src.main.requests.post')
    def test_audio_to_text_timeout(self, mock_post, workspace_with_audio):
        """测试请求超时"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = audio_to_text()

        assert "error" in result
        assert result["error"]["code"] == "TIMEOUT"
        assert "超时" in result["error"]["message"]

    @patch('src.main.requests.post')
    def test_audio_to_text_connection_error(self, mock_post, workspace_with_audio):
        """测试连接错误"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = audio_to_text()

        assert "error" in result
        assert result["error"]["code"] == "CONNECTION_ERROR"
        assert "无法连接" in result["error"]["message"]

    @patch('src.main.requests.post')
    def test_audio_to_text_parse_error(self, mock_post, workspace_with_audio):
        """测试响应解析错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = audio_to_text()

        assert "error" in result
        assert result["error"]["code"] == "PARSE_ERROR"
        assert "解析" in result["error"]["message"]

    def test_audio_to_text_single_file_only(self, workspace):
        """测试只处理第一个文件（即使有多个文件）"""
        inputs_dir = workspace / "data" / "inputs" / "input"

        # 创建多个模拟音频文件
        (inputs_dir / "audio1.wav").write_bytes(b"fake audio 1")
        (inputs_dir / "audio2.mp3").write_bytes(b"fake audio 2")
        (inputs_dir / "audio3.WAV").write_bytes(b"fake audio 3")

        with patch('src.main.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": [{
                    "key": "test.wav",
                    "text": "test",
                    "clean_text": "test"
                }]
            }
            mock_post.return_value = mock_response

            result = audio_to_text()

            # 确保只处理了一个文件（文件名是3个中的一个）
            assert "error" not in result
            assert "filename" in result
            assert result["filename"] in ["audio1.wav", "audio2.mp3", "audio3.WAV"]
            # 验证requests.post只被调用了一次（只处理一个文件）
            assert mock_post.call_count == 1

    def test_audio_to_text_valid_languages(self, workspace_with_audio):
        """测试所有支持的语言参数"""
        valid_languages = ["auto", "zh", "en", "yue", "ja", "ko", "nospeech"]

        with patch('src.main.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": [{"text": "test", "clean_text": "test"}]
            }
            mock_post.return_value = mock_response

            for lang in valid_languages:
                result = audio_to_text(lang=lang)
                assert "error" not in result
                assert result["language"] == lang
