# Prefab 文件处理指南 v3.0

> v3.0 架构：文件独立化 + 输出数组化

## 🎯 核心原则

### 文件独立于参数

**设计理念**：
- 文件不是"参数"，而是 HTTP 请求中的"附件"
- 更清晰的职责分离：`files` vs `parameters`
- 更接近真实的网络请求语义（multipart/form-data）

## 📋 Manifest 定义（v3.0）

### 基本结构

```json
{
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
          "default": "mp3"
        }
      ],
      "returns": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "duration": {"type": "number"}
        }
      }
    }
  ]
}
```

### 多个文件组（高级用法）

```json
{
  "files": {
    "video": {
      "type": "array",
      "items": {"type": "InputFile"},
      "description": "输入视频",
      "minItems": 1,
      "maxItems": 1
    },
    "watermark": {
      "type": "array",
      "items": {"type": "InputFile"},
      "description": "水印图片",
      "minItems": 1,
      "maxItems": 1
    },
    "output": {
      "type": "array",
      "items": {"type": "OutputFile"},
      "description": "带水印的视频"
    }
  },
  "parameters": [
    {"name": "position", "type": "string", "default": "bottom-right"}
  ]
}
```

## 💻 Prefab 代码

### 基本示例

```python
from pathlib import Path

DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")

def video_to_audio(audio_format: str = "mp3") -> dict:
    """
    将视频转换为音频（v3.0 架构）
    
    ⚠️ 注意：不再有文件参数！
    
    Args:
        audio_format: 音频格式（纯业务参数）
    
    Returns:
        业务结果（不包含文件路径）
    """
    # 1. 自动扫描 data/inputs 目录
    input_files = list(DATA_INPUTS.glob("*"))
    if not input_files:
        return {"success": False, "error": "No input files"}
    
    video_file = input_files[0]
    
    # 2. 处理文件
    audio_clip = extract_audio(video_file)
    duration = audio_clip.duration
    
    # 3. 写入 data/outputs（Gateway 会自动上传）
    output_file = DATA_OUTPUTS / f"{video_file.stem}.{audio_format}"
    DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
    audio_clip.save(output_file)
    
    # 4. 返回业务结果（不包含文件路径）
    return {
        "success": True,
        "format": audio_format,
        "duration": duration
    }
```

### 多个文件组（高级用法）

```python
def add_watermark(position: str = "bottom-right") -> dict:
    """
    为视频添加水印
    
    文件组织：
    - data/inputs/video/       ← files.video
    - data/inputs/watermark/   ← files.watermark
    - data/outputs/            ← files.output
    """
    # 读取不同文件组
    video_files = list(Path("data/inputs/video").glob("*"))
    watermark_files = list(Path("data/inputs/watermark").glob("*"))
    
    video = video_files[0]
    watermark = watermark_files[0]
    
    # 处理...
    result_video = add_watermark_to_video(video, watermark, position)
    
    # 写入输出
    output_file = Path("data/outputs/watermarked.mp4")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_video.save(output_file)
    
    return {"success": True, "position": position}
```

## 🔄 完整数据流

### 1. 用户调用（Frontend）

```typescript
{
  prefab_id: "video-processing-prefab",
  version: "0.3.0",
  function_name: "video_to_audio",
  files: {
    input: ["s3://bucket/user-uploads/video.mp4"]
  },
  parameters: {
    audio_format: "mp3"
  }
}
```

### 2. Gateway 处理

```python
# 下载文件
download_files(files["input"], workspace / "data/inputs")
# 或多个文件组：
# download_files(files["video"], workspace / "data/inputs/video")
# download_files(files["watermark"], workspace / "data/inputs/watermark")

# 调用 Prefab（只传 parameters）
result = call_prefab(parameters)

# 扫描输出
output_files = scan_and_upload(workspace / "data/outputs")

# 响应
return {
  "output": result,
  "files": {"output": output_files}
}
```

### 3. Prefab 执行

```python
# 不接收文件参数，只接收业务参数
def video_to_audio(audio_format: str):
    # 自动扫描输入
    video = list(Path("data/inputs").glob("*"))[0]
    
    # 处理
    audio = convert(video, audio_format)
    
    # 写入输出
    audio.save(Path("data/outputs/audio.mp3"))
    
    # 返回业务结果
    return {"success": True}
```

### 4. 最终响应

```json
{
  "status": "SUCCESS",
  "output": {
    "success": true,
    "format": "mp3",
    "duration": 60.0
  },
  "files": {
    "output": ["s3://bucket/prefab-outputs/2025/10/21/audio.mp3"]
  }
}
```

## 📊 v2.0 vs v3.0 对比

| 特性 | v2.0 | v3.0 |
|------|------|------|
| 文件位置 | `parameters.input_files` | `files.input` |
| 函数签名 | `func(input_files: List[str], format: str)` | `func(format: str)` |
| 输入方式 | 传入文件名列表 | 自动扫描目录 |
| 输出方式 | 返回文件路径 | 自动扫描目录 |
| 输出格式 | 单个文件（不统一） | 统一数组 |
| 职责分离 | 模糊 | 清晰 |
| 多文件组 | ❌ 不支持 | ✅ 支持 |

## 🌟 v3.0 优势

### 1. 更清晰的语义

```python
# v2.0: 文件混在参数里
def func(input_files: List[str], watermark: List[str], format: str):
    # 哪些是文件？哪些是参数？不够清晰

# v3.0: 完全分离
def func(format: str):
    # 参数一目了然！
    # 文件由 Gateway 管理，Prefab 只关心业务逻辑
```

### 2. 更简单的开发体验

```python
# v2.0: 需要手动处理文件名
def func(input_files: List[str]):
    for filename in input_files:
        path = DATA_INPUTS / filename
        process(path)

# v3.0: 直接扫描
def func():
    for file in DATA_INPUTS.glob("*"):
        process(file)
```

### 3. 支持多个文件组

```
data/inputs/
  ├─ video/         ← files.video
  ├─ watermark/     ← files.watermark
  └─ subtitle/      ← files.subtitle
```

### 4. 统一的输出格式

```json
// 所有 Prefab 的输出都是统一的
{
  "output": {...},        // 业务结果
  "files": {              // 文件输出（统一数组）
    "output": ["s3://..."]
  }
}
```

## 🔧 迁移指南

### Manifest 迁移

**移除**：
```json
"parameters": [
  {
    "name": "input_files",
    "type": "array",
    "items": {"type": "InputFile"}
  }
]
```

**添加**：
```json
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
}
```

### 代码迁移

**移除文件参数**：
```python
# v2.0
def func(input_files: List[str], format: str):
    ...

# v3.0
def func(format: str):  # ← 移除 input_files
    ...
```

**自动扫描输入**：
```python
# v2.0
input_path = DATA_INPUTS / input_files[0]

# v3.0
input_files = list(DATA_INPUTS.glob("*"))
input_path = input_files[0]
```

**不返回文件路径**：
```python
# v2.0
return {
  "output_file": "data/outputs/result.mp3"
}

# v3.0
return {
  "format": "mp3",
  "duration": 60.0
  # Gateway 会自动扫描 data/outputs/ 并返回文件
}
```

## ⚠️ 注意事项

### 1. 破坏性更新

v3.0 不向后兼容 v2.0：
- Manifest 格式不同
- 函数签名不同
- API 请求/响应格式不同

### 2. 版本号规范

采用 v3.0 架构的 Prefab 应使用版本号 >= 0.3.0

### 3. Gateway 依赖

v3.0 Prefab 需要 Gateway v3.0+ 支持

## 📚 示例代码

### 单文件处理

```python
def process_text(operation: str = "uppercase") -> dict:
    # 扫描输入
    files = list(Path("data/inputs").glob("*"))
    content = files[0].read_text()
    
    # 处理
    result = content.upper() if operation == "uppercase" else content.lower()
    
    # 写入输出
    Path("data/outputs/result.txt").write_text(result)
    
    # 返回业务数据
    return {"operation": operation, "length": len(result)}
```

### 多文件处理

```python
def concat_videos() -> dict:
    # 扫描所有输入视频
    videos = list(Path("data/inputs").glob("*.mp4"))
    
    # 合并
    result = concatenate(videos)
    
    # 输出
    result.save(Path("data/outputs/merged.mp4"))
    
    return {"count": len(videos), "duration": result.duration}
```

### 多文件组处理

```python
def add_watermark(position: str = "bottom-right") -> dict:
    # 不同的文件组
    video = list(Path("data/inputs/video").glob("*"))[0]
    watermark = list(Path("data/inputs/watermark").glob("*"))[0]
    
    # 处理
    result = overlay(video, watermark, position)
    
    # 输出
    result.save(Path("data/outputs/watermarked.mp4"))
    
    return {"position": position}
```

## 🧪 测试示例

```python
def test_process_text_file():
    # v3.0: 不传入文件参数
    result = process_text_file(operation="uppercase")
    
    # 验证业务结果
    assert result["success"] is True
    assert result["operation"] == "uppercase"
    
    # v3.0: 返回值不包含文件路径
    assert "output_file" not in result
    
    # 验证输出文件存在
    output_files = list(Path("data/outputs").glob("*"))
    assert len(output_files) >= 1
```

## 🔗 相关文档

- [ARCHITECTURE_V3.md](ARCHITECTURE_V3.md) - 完整架构设计
- [PREFAB_GUIDE.md](PREFAB_GUIDE.md) - 开发指南
- [FILE_HANDLING_GUIDE.md](FILE_HANDLING_GUIDE.md) - v2.0 文档（已废弃）

---

**版本**: v3.0  
**更新日期**: 2025-10-21  
**状态**: ✅ 已实现

