# Prefab 文件处理指南

> 本指南介绍如何在 Prefab 中处理文件输入和输出

## 📁 核心约定

### 路径规范

```
workspace/
  ├── data/
  │   ├── inputs/          # 所有输入文件
  │   │   ├── video.mp4    # Gateway 下载的原始文件
  │   │   ├── image.jpg
  │   │   └── ...
  │   └── outputs/         # 所有输出文件
  │       ├── audio.mp3    # Prefab 生成的文件
  │       ├── result.mp4
  │       └── ...
```

### 关键原则

1. **固定路径**：输入始终在 `data/inputs/`，输出始终在 `data/outputs/`
2. **文件名列表**：所有文件参数都是列表形式（即使只有一个文件）
3. **保留原名**：Gateway 下载时保留用户上传的原始文件名
4. **相对路径返回**：Prefab 返回相对于 workspace 的路径，Gateway 自动替换为 S3 URL

---

## 🎯 工作流程

### 1. 用户上传文件

```
用户 → 前端 → S3
       上传 1.mp4 到 s3://bucket/prefab-inputs/user-123/1.mp4
```

### 2. Gateway 下载文件

```python
# Gateway 接收调用
{
  "prefab_id": "video-processing",
  "function_name": "video_to_audio",
  "inputs": {
    "input_files": ["s3://bucket/.../1.mp4"]  # S3 URL 列表
  }
}

# Gateway 下载到 PVC
workspace/data/inputs/1.mp4  # 保留原文件名

# Gateway 调用 Prefab
{
  "inputs": {
    "input_files": ["1.mp4"]  # 传递文件名列表
  },
  "workspace": "/mnt/prefab-workspace/request-xxx"
}
```

### 3. Prefab 处理文件

```python
from pathlib import Path
from typing import List

DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")

def video_to_audio(input_files: List[str], format: str = "mp3"):
    # 获取输入文件
    video_filename = input_files[0]  # "1.mp4"
    video_path = DATA_INPUTS / video_filename
    
    # 生成输出文件
    DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
    audio_path = DATA_OUTPUTS / f"audio.{format}"
    
    # 处理...
    
    # 返回相对路径
    return {
        "success": True,
        "output_file": "data/outputs/audio.mp3"  # 相对路径
    }
```

### 4. Gateway 上传输出

```python
# Gateway 扫描 data/outputs/ 目录
workspace/data/outputs/audio.mp3

# 上传到 S3
s3://bucket/prefab-outputs/2025/10/21/request-xxx/uuid.mp3

# 替换返回值中的路径
{
  "success": True,
  "output_file": "s3://bucket/.../uuid.mp3"  # S3 URL
}
```

---

## 💻 代码示例

### 示例 1：单文件处理

```python
from pathlib import Path
from typing import List

DATA_INPUTS = Path("data/inputs")
DATA_OUTPUTS = Path("data/outputs")


def video_to_audio(input_files: List[str], format: str = "mp3") -> dict:
    """
    将视频转换为音频
    
    Args:
        input_files: 输入视频文件名列表（只取第一个）
        format: 输出格式
    
    Returns:
        包含输出文件路径的字典
    """
    try:
        # 1. 获取输入文件
        video_filename = input_files[0]
        video_path = DATA_INPUTS / video_filename
        
        if not video_path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {video_filename}"
            }
        
        # 2. 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        
        # 3. 处理文件
        audio_path = DATA_OUTPUTS / f"audio.{format}"
        
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(str(video_path))
        video.audio.write_audiofile(str(audio_path))
        video.close()
        
        # 4. 返回相对路径（Gateway 会自动替换为 S3 URL）
        return {
            "success": True,
            "output_file": f"data/outputs/audio.{format}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 示例 2：多文件处理

```python
def concatenate_videos(input_files: List[str]) -> dict:
    """
    拼接多个视频
    
    Args:
        input_files: 输入视频文件名列表（至少2个）
    
    Returns:
        包含输出文件路径的字典
    """
    try:
        if len(input_files) < 2:
            return {
                "success": False,
                "error": "至少需要2个视频文件"
            }
        
        # 1. 加载所有输入文件
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        
        clips = []
        for filename in input_files:
            video_path = DATA_INPUTS / filename
            if not video_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {filename}"
                }
            clips.append(VideoFileClip(str(video_path)))
        
        # 2. 拼接视频
        final = concatenate_videoclips(clips)
        
        # 3. 输出
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        output_path = DATA_OUTPUTS / "result.mp4"
        final.write_videofile(str(output_path))
        
        # 清理
        for clip in clips:
            clip.close()
        final.close()
        
        # 4. 返回相对路径
        return {
            "success": True,
            "output_file": "data/outputs/result.mp4"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 示例 3：多个输出文件

```python
def extract_frames(input_files: List[str], times: List[float]) -> dict:
    """
    从视频提取帧
    
    Args:
        input_files: 输入视频文件名列表（只取第一个）
        times: 时间点列表（秒）
    
    Returns:
        包含多个输出文件路径的字典
    """
    try:
        video_filename = input_files[0]
        video_path = DATA_INPUTS / video_filename
        
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(str(video_path))
        
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)
        
        frame_files = []
        for i, t in enumerate(times):
            # 保存帧
            frame_path = DATA_OUTPUTS / f"frame_{i:03d}.jpg"
            video.save_frame(str(frame_path), t=t)
            
            # 记录相对路径
            frame_files.append(f"data/outputs/frame_{i:03d}.jpg")
        
        video.close()
        
        return {
            "success": True,
            "frame_count": len(frame_files),
            "frames": frame_files  # 路径列表
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 📋 Manifest 定义

### 单文件输入

```json
{
  "name": "video_to_audio",
  "parameters": [
    {
      "name": "input_files",
      "type": "array",
      "items": {"type": "InputFile"},
      "minItems": 1,
      "maxItems": 1,
      "description": "输入视频文件（只需要1个）",
      "required": true
    }
  ]
}
```

### 多文件输入

```json
{
  "name": "concatenate_videos",
  "parameters": [
    {
      "name": "input_files",
      "type": "array",
      "items": {"type": "InputFile"},
      "minItems": 2,
      "description": "输入视频文件列表（至少2个）",
      "required": true
    }
  ]
}
```

### 文件输出

```json
{
  "returns": {
    "type": "object",
    "properties": {
      "output_file": {
        "type": "string",
        "description": "输出文件路径（Gateway 会自动替换为 S3 URL）"
      }
    }
  }
}
```

---

## ⚠️ 注意事项

### ✅ 正确的做法

1. **使用固定路径**
   ```python
   DATA_INPUTS = Path("data/inputs")
   DATA_OUTPUTS = Path("data/outputs")
   ```

2. **参数统一用列表**
   ```python
   def process(input_files: List[str]):  # ✅
       filename = input_files[0]
   ```

3. **返回相对路径**
   ```python
   return {"output_file": "data/outputs/result.mp4"}  # ✅
   ```

4. **创建输出目录**
   ```python
   DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)  # ✅
   ```

### ❌ 错误的做法

1. **硬编码文件名**
   ```python
   video_path = Path("1.mp4")  # ❌ 用户上传的文件名可能不同
   ```

2. **使用单个字符串参数**
   ```python
   def process(input_file: str):  # ❌ 应该用 List[str]
   ```

3. **返回绝对路径**
   ```python
   return {"output_file": "/mnt/prefab-workspace/.../result.mp4"}  # ❌
   ```

4. **不检查文件存在**
   ```python
   video = VideoFileClip(str(video_path))  # ❌ 应先检查 .exists()
   ```

---

## 🧪 本地测试

```python
# test_local.py
from pathlib import Path
from src.main import video_to_audio

# 创建测试环境
workspace = Path("test_workspace")
(workspace / "data/inputs").mkdir(parents=True, exist_ok=True)

# 准备测试文件
import shutil
shutil.copy("test.mp4", workspace / "data/inputs/test.mp4")

# 切换到工作目录
import os
os.chdir(workspace)

# 调用函数
result = video_to_audio(input_files=["test.mp4"], format="mp3")
print(result)

# 检查输出
assert result["success"] is True
assert Path(result["output_file"]).exists()
```

---

## 📚 常见问题

**Q: 为什么所有文件参数都是列表？**  
A: 统一格式，简化代码模式。单文件场景取 `[0]`，多文件场景直接遍历。

**Q: 输出文件名可以自定义吗？**  
A: 可以，只要在 `data/outputs/` 目录下即可。建议使用语义化的名称。

**Q: 如何处理大文件？**  
A: Gateway 已经配置了分片上传/下载，Prefab 无需特殊处理。

**Q: 输出多个文件怎么办？**  
A: Gateway 会自动扫描 `data/outputs/` 并上传所有文件，只需返回路径列表。

**Q: 可以在子目录中输出文件吗？**  
A: 可以，如 `data/outputs/frames/frame_001.jpg`，Gateway 会递归上传。

---

## 🔗 相关文档

- [README.md](README.md) - 项目概览
- [PREFAB_GUIDE.md](PREFAB_GUIDE.md) - 完整开发指南
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

