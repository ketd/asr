# Prefab 架构 v3.0 设计文档

> 文件独立化 + 输出数组化

## 🎯 核心变更

### 1. 文件独立于参数
**理念**：文件不是"参数"，是 HTTP 请求中的"附件"

**v2.0（旧）**：
```json
{
  "parameters": [
    {
      "name": "input_files",
      "type": "array",
      "items": {"type": "InputFile"}
    },
    {
      "name": "format",
      "type": "string"
    }
  ]
}
```

**v3.0（新）**：
```json
{
  "files": {
    "input": {
      "type": "array",
      "items": {"type": "InputFile"},
      "description": "输入文件",
      "required": true,
      "minItems": 1,
      "maxItems": 10
    },
    "output": {
      "type": "array",
      "items": {"type": "OutputFile"},
      "description": "输出文件"
    }
  },
  "parameters": [
    {
      "name": "format",
      "type": "string"
    }
  ]
}
```

### 2. 输出文件统一为数组

**v2.0（旧）**：
```json
"returns": {
  "properties": {
    "output_file": {"type": "OutputFile"}  // 单个
  }
}
```

**v3.0（新）**：
```json
"files": {
  "output": {
    "type": "array",
    "items": {"type": "OutputFile"}  // 统一数组
  }
}
```

## 📋 完整示例

### Manifest v3.0

```json
{
  "version": "3.0",
  "id": "video-processing-prefab",
  "name": "视频处理工具",
  "functions": [
    {
      "name": "video_to_audio",
      "description": "将视频转换为音频",
      "files": {
        "input": {
          "type": "array",
          "items": {"type": "InputFile"},
          "description": "输入视频文件",
          "required": true,
          "minItems": 1,
          "maxItems": 1
        },
        "output": {
          "type": "array",
          "items": {"type": "OutputFile"},
          "description": "输出音频文件"
        }
      },
      "parameters": [
        {
          "name": "audio_format",
          "type": "string",
          "description": "音频格式",
          "default": "mp3",
          "enum": ["mp3", "wav", "aac"]
        }
      ],
      "returns": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "format": {"type": "string"},
          "duration": {"type": "number"}
        }
      }
    }
  ]
}
```

### Prefab 函数签名

```python
from pathlib import Path
from typing import List

DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")

def video_to_audio(audio_format: str = "mp3") -> dict:
    """
    将视频转换为音频
    
    文件约定：
    - 输入文件：自动在 data/inputs/ 下（Gateway 下载）
    - 输出文件：写入 data/outputs/（Gateway 自动上传）
    
    Args:
        audio_format: 音频格式（不再包含文件参数！）
    
    Returns:
        处理结果（不包含文件路径！）
    """
    # 扫描 data/inputs 获取文件
    input_files = list(DATA_INPUTS.glob("*"))
    if not input_files:
        return {"success": False, "error": "No input files"}
    
    video_file = input_files[0]
    
    # 处理...
    output_file = DATA_OUTPUTS / f"{video_file.stem}.{audio_format}"
    
    # 保存到 data/outputs/
    # Gateway 会自动扫描并上传
    
    return {
        "success": True,
        "format": audio_format,
        "duration": 60.0
        # 不返回文件路径！
    }
```

### Gateway 调用格式

**请求**：
```json
{
  "prefab_id": "video-processing-prefab",
  "version": "0.3.0",
  "function_name": "video_to_audio",
  "files": {
    "input": ["s3://bucket/path/to/video.mp4"]
  },
  "parameters": {
    "audio_format": "mp3"
  }
}
```

**响应**：
```json
{
  "status": "SUCCESS",
  "output": {
    "success": true,
    "format": "mp3",
    "duration": 60.0
  },
  "files": {
    "output": ["s3://bucket/path/to/audio.mp3"]
  }
}
```

## 🔄 数据流

### 1. 用户调用
```
Frontend:
{
  files: { input: ["s3://video.mp4"] },
  parameters: { audio_format: "mp3" }
}
```

### 2. Gateway 处理
```python
# 1. 下载 files.input 到 workspace/data/inputs/
download_files(files["input"], workspace / "data/inputs")

# 2. 调用 Prefab（只传参数）
prefab_result = call_prefab(parameters)

# 3. 扫描 workspace/data/outputs/
output_files = scan_outputs(workspace / "data/outputs")

# 4. 上传到 S3
output_urls = upload_to_s3(output_files)

# 5. 返回
return {
  "output": prefab_result,
  "files": {"output": output_urls}
}
```

### 3. Prefab 处理
```python
def video_to_audio(audio_format: str = "mp3"):
    # 读取 data/inputs/
    video = list(Path("data/inputs").glob("*"))[0]
    
    # 处理
    audio = convert(video, audio_format)
    
    # 写入 data/outputs/
    audio.save(Path("data/outputs") / f"audio.{audio_format}")
    
    # 返回结果（无文件路径）
    return {"success": True, "format": audio_format}
```

## ✨ 优势

### 1. 清晰的职责分离
```
files:       Gateway 管理
parameters:  Prefab 处理
```

### 2. 更接近 HTTP 语义
```
HTTP multipart/form-data:
- files: 附件
- data: 表单数据

Prefab v3.0:
- files: 文件
- parameters: 参数
```

### 3. 简化 Prefab 开发
```python
# v2.0: 需要处理文件参数
def func(input_files: List[str], format: str):
    for file in input_files:
        video = load(DATA_INPUTS / file)
        
# v3.0: 只关注业务逻辑
def func(format: str):
    for video in DATA_INPUTS.glob("*"):
        # 直接处理
```

### 4. 统一的文件处理
```
输入：数组 ✅
输出：数组 ✅
扩展性：统一 ✅
```

## 🔧 迁移指南

### Manifest 迁移

**v2.0**：
```json
{
  "parameters": [
    {"name": "input_files", "type": "array", "items": {"type": "InputFile"}},
    {"name": "format", "type": "string"}
  ],
  "returns": {
    "properties": {
      "output_file": {"type": "string"}
    }
  }
}
```

**v3.0**：
```json
{
  "files": {
    "input": {
      "type": "array",
      "items": {"type": "InputFile"},
      "minItems": 1,
      "maxItems": 1
    },
    "output": {
      "type": "array",
      "items": {"type": "OutputFile"}
    }
  },
  "parameters": [
    {"name": "format", "type": "string"}
  ],
  "returns": {
    "properties": {
      "format": {"type": "string"}
    }
  }
}
```

### 代码迁移

**v2.0**：
```python
def video_to_audio(input_files: List[str], audio_format: str = "mp3") -> dict:
    video_filename = input_files[0]
    video_path = DATA_INPUTS / video_filename
    # ...
    return {
        "output_file": str(output_path.relative_to(...))
    }
```

**v3.0**：
```python
def video_to_audio(audio_format: str = "mp3") -> dict:
    # 自动扫描 data/inputs
    videos = list(DATA_INPUTS.glob("*"))
    video_path = videos[0]
    # ...
    # 写入 data/outputs（不返回路径）
    return {
        "format": audio_format,
        "duration": 60.0
    }
```

## 📊 版本对比

| 特性 | v2.0 | v3.0 |
|------|------|------|
| 文件位置 | parameters | files |
| 输出格式 | 单个/不统一 | 统一数组 |
| 函数签名 | 包含文件参数 | 纯业务参数 |
| 文件路径 | 手动管理 | 自动扫描 |
| 职责分离 | 模糊 | 清晰 |
| HTTP 语义 | 不明确 | 明确 |

## 🎯 实施计划

1. ✅ 架构设计（本文档）
2. 📝 Template 更新
3. 🔧 Gateway 适配
4. 🏭 Factory 适配  
5. 🎬 Video-processing 迁移
6. 🖼️ Frontend 适配
7. 🧪 全面测试

---

**版本**: v3.0  
**状态**: 设计完成  
**下一步**: 实施

