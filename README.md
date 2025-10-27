# 🎤 ASR 语音识别预制件 (ASR Prefab)

[![Build and Release](https://github.com/your-org/asr-prefab/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/your-org/asr-prefab/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/managed%20by-uv-F67909.svg)](https://github.com/astral-sh/uv)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black)](https://flake8.pycqa.org/)

> **将音频文件转换为文字的 AI 预制件。支持多种语言（中文、英文、粤语、日语、韩语）和音频格式（WAV、MP3）。**

## 📋 目录

- [功能介绍](#功能介绍)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [API 参数](#api-参数)
- [错误处理](#错误处理)
- [开发指南](#开发指南)
- [测试与验证](#测试与验证)
- [常见问题](#常见问题)

**📚 更多文档**: [文档索引](DOCS_INDEX.md) | [架构设计](ARCHITECTURE.md) | [AI助手指南](AGENTS.md)

## 功能介绍

这个预制件封装了 ASR (Automatic Speech Recognition，自动语音识别) 服务，可以将音频文件转换为文字。

### 核心功能

- 🎤 **多语言支持**: 中文、英文、粤语、日语、韩语，支持自动检测
- 🎵 **多格式支持**: WAV、MP3 音频格式
- 📦 **批量处理**: 支持同时处理多个音频文件
- ⚡ **高效转换**: 基于专业的 ASR 服务引擎
- 🔄 **自动重试**: 包含完善的错误处理机制
- 🌐 **灵活配置**: 支持通过环境变量配置 API 地址

### 支持的语言

| 语言代码 | 语言名称 | 说明 |
|---------|---------|------|
| `auto` | 自动检测 | 自动识别音频语言（默认） |
| `zh` | 中文 | 普通话 |
| `en` | 英语 | English |
| `yue` | 粤语 | 广东话 |
| `ja` | 日语 | 日本語 |
| `ko` | 韩语 | 한국어 |
| `nospeech` | 无语音 | 仅用于标记无语音内容 |

### 支持的音频格式

- **WAV**: 推荐 16KHz 采样率
- **MP3**: 推荐 16KHz 采样率

### 技术架构

- **基于 v3.0 架构**: 符合最新的预制件规范
- **文件自动管理**: Gateway 自动处理文件上传和下载
- **标准化输出**: 统一的响应格式，便于 AI 解析

## 快速开始

### 1. 前置要求

- Python 3.11+
- ASR 服务地址（默认: `http://192.168.1.218:50000/api/v1/asr`）
- [uv](https://github.com/astral-sh/uv) 包管理工具

### 2. 安装

克隆仓库并安装依赖：

```bash
git clone https://github.com/your-org/asr-prefab.git
cd asr-prefab

# 安装 uv（如果尚未安装）
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖（自动创建虚拟环境）
uv sync --dev
```

### 3. 配置 ASR 服务地址（可选）

默认使用 `http://192.168.1.218:50000/api/v1/asr`。如需修改，设置环境变量：

```bash
# Linux/macOS
export ASR_API_URL="http://your-asr-service:port/api/v1/asr"

# Windows (CMD)
set ASR_API_URL=http://your-asr-service:port/api/v1/asr

# Windows (PowerShell)
$env:ASR_API_URL="http://your-asr-service:port/api/v1/asr"
```

### 4. 使用示例

在 AI 平台中，上传音频文件并调用 `audio_to_text` 函数：

```python
# AI 会自动将用户上传的音频文件放到 data/inputs/ 目录
# 然后调用函数：

# 自动检测语言
result = audio_to_text()

# 指定中文
result = audio_to_text(lang="zh")

# 指定英文
result = audio_to_text(lang="en")
```

### 5. 本地测试

```bash
# 运行测试
uv run pytest tests/ -v

# 代码风格检查
uv run flake8 src/ --max-line-length=120

# 验证 manifest 一致性
uv run python scripts/validate_manifest.py
```

## 使用示例

### 基本用法

```python
from src.main import audio_to_text

# 1. 自动检测语言（默认）
result = audio_to_text()
print(result)
# {
#   "success": True,
#   "results": [...],  # ASR 服务返回的转录结果
#   "total_files": 1,
#   "language": "auto",
#   "api_url": "http://192.168.1.218:50000/api/v1/asr"
# }

# 2. 指定语言为中文
result = audio_to_text(lang="zh")

# 3. 指定语言为英文
result = audio_to_text(lang="en")

# 4. 指定文件名（多个文件时）
result = audio_to_text(lang="auto", keys="meeting1,meeting2")
```

### AI 集成示例

当部署到 AI 平台后，用户可以这样使用：

> **用户**: "帮我把这段录音转成文字"  
> *[用户上传音频文件 meeting.wav]*  
> **AI**: *调用 `audio_to_text()`*  
> **AI**: "已完成转录：\n\n「你好，欢迎参加今天的会议...」"

> **用户**: "转录这段英文音频"  
> *[用户上传音频文件 podcast.mp3]*  
> **AI**: *调用 `audio_to_text(lang="en")`*  
> **AI**: "转录完成：\n\n「Hello everyone, welcome to today's podcast...」"

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| `ASR_API_URL` | ASR 服务的 API 地址 | `http://192.168.1.218:50000/api/v1/asr` |

### 文件路径约定（v3.0 架构）

| 路径 | 用途 | 说明 |
|------|------|------|
| `data/inputs/` | 输入音频文件 | Gateway 自动下载用户上传的文件到此目录 |
| `data/outputs/` | 输出文件（可选） | 如需生成文件，放到此目录，Gateway 会自动上传 |

## API 参数

### `audio_to_text(lang, keys)`

将音频文件转换为文字。

**参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `lang` | `string` | 否 | `"auto"` | 音频语言，可选值：`auto`, `zh`, `en`, `yue`, `ja`, `ko`, `nospeech` |
| `keys` | `string` | 否 | `""` | 文件名列表（逗号分隔），为空时使用实际文件名 |

**返回值（成功）：**

```python
{
    "success": True,
    "results": [
        # ASR 服务返回的转录结果
        # 具体格式取决于后端 ASR 服务
    ],
    "total_files": 1,
    "language": "auto",
    "api_url": "http://192.168.1.218:50000/api/v1/asr"
}
```

**返回值（失败）：**

```python
{
    "success": False,
    "error": "错误信息",
    "error_code": "ERROR_CODE",
    "details": "详细错误信息（可选）"
}
```

## 错误处理

### 错误代码说明

| 错误代码 | 说明 | 解决方法 |
|---------|------|---------|
| `INVALID_LANGUAGE` | 不支持的语言代码 | 检查 `lang` 参数是否正确 |
| `NO_INPUT_DIR` | 输入目录不存在 | 确保 `data/inputs/` 目录存在 |
| `NO_AUDIO_FILES` | 未找到音频文件 | 确保上传了 .wav 或 .mp3 文件 |
| `FILE_OPEN_ERROR` | 无法打开音频文件 | 检查文件权限和格式 |
| `ASR_API_ERROR` | ASR 服务返回错误 | 检查 ASR 服务状态和配置 |
| `TIMEOUT` | 请求超时 | 音频文件过大或服务响应慢 |
| `CONNECTION_ERROR` | 无法连接 ASR 服务 | 检查网络和服务地址 |
| `REQUEST_ERROR` | 请求失败 | 查看 error 字段了解详情 |
| `PARSE_ERROR` | 解析响应失败 | ASR 服务返回了非 JSON 格式 |
| `UNEXPECTED_ERROR` | 未知错误 | 查看 error 字段了解详情 |

### 示例错误处理

```python
result = audio_to_text(lang="zh")

if not result["success"]:
    error_code = result.get("error_code")
    error_msg = result.get("error")
    
    if error_code == "NO_AUDIO_FILES":
        print("请先上传音频文件")
    elif error_code == "CONNECTION_ERROR":
        print("无法连接到 ASR 服务，请检查配置")
    else:
        print(f"转录失败: {error_msg}")
else:
    print(f"成功转录 {result['total_files']} 个文件")
```

## 开发指南

### 项目结构

```
asr-prefab/
├── .github/
│   └── workflows/
│       └── build-and-release.yml    # CI/CD 自动化流程
├── src/
│   └── main.py                      # ASR 核心代码
├── tests/
│   └── test_main.py                 # 单元测试
├── data/
│   ├── inputs/                      # 输入音频文件目录
│   └── outputs/                     # 输出文件目录（可选）
├── scripts/
│   └── validate_manifest.py         # Manifest 验证脚本
├── prefab-manifest.json             # 预制件元数据
├── pyproject.toml                   # 项目配置和依赖
└── README.md                        # 本文档
```

### 修改 ASR 服务地址

编辑 `src/main.py`，修改默认值：

```python
# ASR 服务配置
ASR_API_URL = os.environ.get("ASR_API_URL", "http://your-new-url:port/api/v1/asr")
    """
    分析数据集并返回统计结果
    
    Args:
        data: 数字列表
        operation: 操作类型 ("statistics", "sum", "average")
    
    Returns:
        包含分析结果的字典
    """
    try:
        if not data:
            return {
                "success": False,
                "error": "数据集不能为空",
                "error_code": "EMPTY_DATA"
            }
        
        if operation == "statistics":
            stats = calculate_statistics(data)
            return {
                "success": True,
                "data": {
                    "operation": "statistics",
                    "statistics": stats
                }
            }
        # ... 其他操作类型
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
```

**编码规范：**

- ✅ 使用类型提示 (Type Hints)
- ✅ 编写清晰的 Docstring
- ✅ 返回结构化的数据（通常是字典）
- ✅ 包含错误处理
- ❌ 避免使用全局状态
- ❌ 不要在模块级别执行副作用操作

### `prefab-manifest.json` - 元数据描述

这是 AI 理解如何调用你的预制件的"API 契约"。**必须**与 `src/main.py` 中的函数签名保持一致。

**字段说明：**

```json
{
  "schema_version": "1.0",           // 清单模式版本（固定）
  "id": "hello-world-prefab",        // 全局唯一的预制件 ID
  "version": "1.0.0",                // 语义化版本号（与 pyproject.toml 和 Git Tag 一致）
  "name": "预制件名称",              // 可读的预制件名称
  "description": "预制件功能描述",    // 详细功能说明
  "tags": ["tag1", "tag2"],          // 标签列表，用于分类和搜索
  "entry_point": "src/main.py",      // 入口文件（固定）
  "dependencies_file": "pyproject.toml",  // 依赖文件（固定）
  "functions": [                     // 函数列表
    {
      "name": "analyze_dataset",     // 函数名（必须与代码一致）
      "description": "分析数据集并返回统计结果",  // 功能描述
      "parameters": [                // 参数列表
        {
          "name": "data",
          "type": "array",           // 使用 JSON Schema 类型名
          "description": "数字列表",
          "required": true
        },
        {
          "name": "operation",
          "type": "string",          // 使用 JSON Schema 类型名
          "description": "操作类型：'statistics', 'sum', 'average'",
          "required": false,
          "default": "statistics"
        }
      ],
      "returns": {                   // 返回值描述（结构化 schema）
        "type": "object",
        "description": "返回结果对象",
        "properties": {
          "success": {
            "type": "boolean",
            "description": "操作是否成功"
          },
          "data": {
            "type": "object",
            "description": "成功时的结果数据",
            "optional": true
          },
          "error": {
            "type": "string",
            "description": "错误信息",
            "optional": true
          },
          "error_code": {
            "type": "string",
            "description": "错误代码",
            "optional": true
          }
        }
      }
    }
  ],
  "execution_environment": {         // 执行环境配置（可选）
    "cpu": "1",                      // CPU 核心数
    "memory": "512Mi"                // 内存大小
  }
}
```

**支持的类型（v2.2 类型系统）：**

*基础类型（对应 JSON Schema）：*
- `string` - 字符串
- `number` - 数字（整数或浮点数）
- `integer` - 整数
- `boolean` - 布尔值
- `object` - 对象/字典
- `array` - 数组/列表

*平台感知类型（用于文件处理）：*
- `InputFile` - 输入文件（平台会自动下载并传递本地路径）
- `OutputFile` - 输出文件（平台会自动上传返回的文件路径）

### 密钥管理（Secrets）- v3.0 新特性

如果你的预制件需要使用 API Key、数据库连接字符串等敏感信息，可以在函数定义中声明 `secrets` 字段。平台会引导用户配置这些密钥，并在运行时自动注入到环境变量中。

**在 manifest.json 中声明 secrets：**

```json
{
  "functions": [
    {
      "name": "fetch_weather",
      "description": "获取城市天气信息",
      "parameters": [...],
      "secrets": [
        {
          "name": "WEATHER_API_KEY",
          "description": "用于认证天气服务的 API 密钥",
          "instructions": "请访问 https://www.weather-provider.com/api-keys 注册并获取您的免费 API Key",
          "required": true
        }
      ]
    }
  ]
}
```

**在代码中使用 secrets：**

```python
import os

def fetch_weather(city: str) -> dict:
    """获取城市天气信息"""
    # 从环境变量中读取密钥（平台会自动注入）
    api_key = os.environ.get('WEATHER_API_KEY')
    
    if not api_key:
        return {
            "success": False,
            "error": "未配置 WEATHER_API_KEY",
            "error_code": "MISSING_API_KEY"
        }
    
    # 使用 API Key 调用第三方服务
    # response = requests.get(api_url, headers={"Authorization": f"Bearer {api_key}"})
    ...
```

**Secrets 字段规范：**

- `name` (必需): 密钥名称，必须是大写字母、数字和下划线（如 `API_KEY`, `DATABASE_URL`）
- `description` (必需): 密钥用途的简短描述
- `instructions` (推荐): 指导用户如何获取该密钥的说明
- `required` (必需): 布尔值，标识该密钥是否为必需

本模板包含完整的 secrets 使用示例，详见 `src/main.py` 中的 `fetch_weather` 函数。

### 依赖管理

在 `pyproject.toml` 中添加你的依赖：

```toml
[project]
# 运行时依赖（会被打包到最终产物中）
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
# 开发/测试依赖（不会被打包）
dev = [
    "pytest>=7.4.0",
    "flake8>=6.1.0",
    "pytest-cov>=4.1.0",
]
```

**使用 uv 管理依赖：**

```bash
# 添加运行时依赖
uv add requests pandas

# 添加开发依赖
uv add --dev pytest flake8

# 同步依赖
uv sync --dev
```

## 测试与验证

### 单元测试

运行测试：

```bash
# 运行所有测试
uv run pytest tests/ -v

# 查看测试覆盖率
uv run pytest tests/ --cov=src --cov-report=html
```

### Manifest 验证

验证 `prefab-manifest.json` 与代码的一致性：

```bash
uv run python scripts/validate_manifest.py
```

## 发布流程

### 版本升级

使用脚本自动升级版本号：

```bash
# 修复版本 (0.1.0 -> 0.1.1)
uv run python scripts/version_bump.py patch

# 功能版本 (0.1.0 -> 0.2.0)
uv run python scripts/version_bump.py minor

# 主版本 (0.1.0 -> 1.0.0)
uv run python scripts/version_bump.py major
```

### 发布到 GitHub

```bash
# 提交更改
git add .
git commit -m "Release v0.2.0"

# 创建 tag
git tag v0.2.0

# 推送
git push origin v0.2.0
```

GitHub Actions 会自动构建并发布 Release。

## 常见问题

### Q: ASR 服务返回什么格式的数据？

**A**: 这取决于你使用的 ASR 服务后端。本预制件会将 ASR 服务的原始响应放在 `results` 字段中返回。请查看你的 ASR 服务文档了解具体格式。

### Q: 支持哪些音频格式？

**A**: 目前支持 WAV 和 MP3 格式。推荐使用 16KHz 采样率的音频以获得最佳识别效果。

### Q: 如何修改 ASR 服务地址？

**A**: 有两种方式：

1. **通过环境变量**（推荐）：
```bash
export ASR_API_URL="http://your-service:port/api/v1/asr"
```

2. **修改代码**：编辑 `src/main.py` 中的默认值。

### Q: 可以同时处理多个音频文件吗？

**A**: 可以！将多个音频文件都上传到 `data/inputs/` 目录，预制件会自动处理所有文件并返回结果。

### Q: 转录超时怎么办？

**A**: 当前超时设置为 5 分钟（300秒）。如果音频文件很大，可能需要增加超时时间。编辑 `src/main.py` 中的 `timeout` 参数：

```python
response = requests.post(
    ASR_API_URL,
    files=files,
    data=data,
    timeout=600  # 修改为 10 分钟
)
```

### Q: 如何获取转录的文本内容？

**A**: ASR 服务的响应格式在 `result["results"]` 中。具体字段取决于你使用的 ASR 服务。一般包含：

```python
result = audio_to_text()
if result["success"]:
    # 访问转录结果
    transcriptions = result["results"]
    # 具体格式请查看你的 ASR 服务文档
```

### Q: 支持实时流式转录吗？

**A**: 当前版本不支持。音频需要完整上传后才能开始转录。如需流式支持，请参考 [STREAMING_GUIDE.md](STREAMING_GUIDE.md) 实现流式函数。

### Q: 如何添加新的语言支持？

**A**: 
1. 确认你的 ASR 服务支持该语言
2. 在 `src/main.py` 的 `valid_languages` 列表中添加语言代码
3. 在 `prefab-manifest.json` 的 `enum` 中添加相同的语言代码
4. 运行验证脚本：`uv run python scripts/validate_manifest.py`

## 贡献指南

欢迎为此模板贡献改进！请：

1. Fork 此仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 支持与反馈

- 📖 [文档](https://github.com/your-org/prefab-template/wiki)
- 🐛 [问题反馈](https://github.com/your-org/prefab-template/issues)
- 💬 [讨论区](https://github.com/your-org/prefab-template/discussions)

---

**祝你开发愉快！🎉**

_如果这个模板对你有帮助，请给我们一个 ⭐ Star！_

