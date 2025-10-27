"""
ASR 预制件核心函数测试

测试语音识别功能，确保函数按预期工作。
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from src.main import audio_to_text


class TestASRFunction:
    """测试 ASR 音频转文字功能"""

    @pytest.fixture
    def workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)

        # 创建目录结构
        inputs_dir = workspace_path / "data" / "inputs"
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
        inputs_dir = workspace / "data" / "inputs"

        # 创建模拟音频文件（空文件，仅用于测试文件扫描）
        audio_file = inputs_dir / "test.wav"
        audio_file.write_bytes(b"fake audio data")

        return workspace

    def test_audio_to_text_invalid_language(self, workspace_with_audio):
        """测试无效的语言参数"""
        result = audio_to_text(lang="invalid_lang")

        assert result["success"] is False
        assert result["error_code"] == "INVALID_LANGUAGE"
        assert "不支持的语言" in result["error"]

    def test_audio_to_text_no_input_dir(self):
        """测试输入目录不存在"""
        # 在一个不存在 data/inputs 的目录中运行
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            result = audio_to_text()

            os.chdir(original_cwd)

            assert result["success"] is False
            assert result["error_code"] == "NO_INPUT_DIR"

    def test_audio_to_text_no_audio_files(self, workspace):
        """测试没有音频文件"""
        result = audio_to_text()

        assert result["success"] is False
        assert result["error_code"] == "NO_AUDIO_FILES"
        assert "未找到音频文件" in result["error"]

    @patch('src.main.requests.post')
    def test_audio_to_text_success(self, mock_post, workspace_with_audio):
        """测试成功转录（模拟 API 响应）"""
        # 模拟 ASR API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "filename": "test.wav",
                "text": "这是一段测试音频",
                "language": "zh"
            }
        ]
        mock_post.return_value = mock_response

        result = audio_to_text(lang="zh")

        assert result["success"] is True
        assert "results" in result
        assert result["total_files"] == 1
        assert result["language"] == "zh"
        assert "api_url" in result

    @patch('src.main.requests.post')
    def test_audio_to_text_with_keys(self, mock_post, workspace_with_audio):
        """测试指定文件名参数"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        result = audio_to_text(lang="auto", keys="meeting1")

        assert result["success"] is True
        # 验证 keys 参数被传递
        call_args = mock_post.call_args
        assert call_args[1]["data"]["keys"] == "meeting1"

    @patch('src.main.requests.post')
    def test_audio_to_text_api_error(self, mock_post, workspace_with_audio):
        """测试 API 返回错误状态码"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = audio_to_text()

        assert result["success"] is False
        assert result["error_code"] == "ASR_API_ERROR"
        assert "HTTP 500" in result["error"]

    @patch('src.main.requests.post')
    def test_audio_to_text_timeout(self, mock_post, workspace_with_audio):
        """测试请求超时"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = audio_to_text()

        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"
        assert "超时" in result["error"]

    @patch('src.main.requests.post')
    def test_audio_to_text_connection_error(self, mock_post, workspace_with_audio):
        """测试连接错误"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = audio_to_text()

        assert result["success"] is False
        assert result["error_code"] == "CONNECTION_ERROR"
        assert "无法连接" in result["error"]

    @patch('src.main.requests.post')
    def test_audio_to_text_parse_error(self, mock_post, workspace_with_audio):
        """测试响应解析错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = audio_to_text()

        assert result["success"] is False
        assert result["error_code"] == "PARSE_ERROR"
        assert "解析" in result["error"]

    def test_audio_to_text_multiple_files(self, workspace):
        """测试多个音频文件"""
        inputs_dir = workspace / "data" / "inputs"

        # 创建多个模拟音频文件
        (inputs_dir / "audio1.wav").write_bytes(b"fake audio 1")
        (inputs_dir / "audio2.mp3").write_bytes(b"fake audio 2")
        (inputs_dir / "audio3.WAV").write_bytes(b"fake audio 3")

        with patch('src.main.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_post.return_value = mock_response

            result = audio_to_text()

            assert result["success"] is True
            assert result["total_files"] == 3

    def test_audio_to_text_valid_languages(self, workspace_with_audio):
        """测试所有支持的语言参数"""
        valid_languages = ["auto", "zh", "en", "yue", "ja", "ko", "nospeech"]

        with patch('src.main.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_post.return_value = mock_response

            for lang in valid_languages:
                result = audio_to_text(lang=lang)
                assert result["success"] is True
                assert result["language"] == lang
