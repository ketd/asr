# 流式函数开发指南

> 本文档详细说明如何在预制件中实现流式返回功能

## 什么是流式函数？

流式函数使用 **生成器（Generator）** 实现，通过 `yield` 逐步返回结果，而不是一次性返回所有数据。客户端通过 **SSE (Server-Sent Events)** 协议实时接收数据。

### 适用场景

- ✅ **LLM 聊天**: 实时显示生成的文本
- ✅ **进度报告**: 长时间任务的进度更新
- ✅ **大数据处理**: 逐行/逐块处理大文件
- ✅ **实时监控**: 持续发送监控数据
- ✅ **日志输出**: 实时查看执行日志

## 快速开始

### 1. 实现生成器函数

```python
from typing import Iterator, Dict, Any

def my_stream_function(param: str) -> Iterator[Dict[str, Any]]:
    """
    流式函数示例
    
    Args:
        param: 参数说明
    
    Yields:
        dict: SSE 事件数据
    """
    try:
        # 开始事件
        yield {"type": "start", "data": {"param": param}}
        
        # 处理并逐步返回
        for i in range(5):
            result = process_data(i)
            yield {"type": "progress", "data": result}
        
        # 完成事件
        yield {"type": "done", "data": {"status": "completed"}}
        
    except Exception as e:
        yield {"type": "error", "data": str(e)}
```

### 2. 配置 Manifest

在 `prefab-manifest.json` 中标记为流式函数：

```json
{
  "functions": [
    {
      "name": "my_stream_function",
      "streaming": true,  // 👈 关键配置
      "description": "流式处理示例",
      "parameters": [
        {
          "name": "param",
          "type": "string",
          "required": true
        }
      ],
      "returns": {
        "type": "object",
        "description": "SSE 事件流"
      }
    }
  ]
}
```

### 3. 运行测试

```python
# tests/test_main.py
def test_my_stream_function():
    result = list(my_stream_function("test"))
    
    # 验证事件顺序
    assert result[0]["type"] == "start"
    assert any(r["type"] == "progress" for r in result)
    assert result[-1]["type"] == "done"
```

## 事件格式规范

### 标准事件类型

所有流式函数应该遵循统一的事件格式：

#### 1. **start** - 开始事件

```python
yield {
    "type": "start",
    "data": {
        "param1": "value1",
        "total": 100,
        "message": "开始处理"
    }
}
```

**用途**: 标识流开始，提供初始信息

#### 2. **progress** - 进度事件

```python
yield {
    "type": "progress",
    "data": {
        "current": 50,
        "total": 100,
        "percentage": 50,
        "message": "正在处理...",
        "result": {...}  # 可选的中间结果
    }
}
```

**用途**: 报告处理进度或中间结果

#### 3. **content** - 内容事件（适用于文本生成）

```python
yield {
    "type": "content",
    "data": "文本片段"
}
```

**用途**: LLM 等场景下的增量文本输出

#### 4. **done** - 完成事件

```python
yield {
    "type": "done",
    "data": {
        "total_processed": 100,
        "success": True,
        "message": "处理完成",
        "summary": {...}  # 可选的汇总信息
    }
}
```

**用途**: 标识流结束，提供最终结果

#### 5. **error** - 错误事件

```python
yield {
    "type": "error",
    "data": "错误描述",
    "error_code": "ERROR_CODE"
}
```

**用途**: 报告执行过程中的错误

## 完整示例

### 示例 1: 进度报告

```python
import time
from typing import Iterator, Dict, Any

def batch_process(items: list) -> Iterator[Dict[str, Any]]:
    """批量处理任务，实时报告进度"""
    try:
        total = len(items)
        
        # 开始
        yield {
            "type": "start",
            "data": {
                "total": total,
                "message": f"开始处理 {total} 个项目"
            }
        }
        
        # 逐个处理
        for i, item in enumerate(items, 1):
            result = process_item(item)
            
            yield {
                "type": "progress",
                "data": {
                    "current": i,
                    "total": total,
                    "percentage": int((i / total) * 100),
                    "item": item,
                    "result": result
                }
            }
            
            time.sleep(0.1)  # 模拟处理时间
        
        # 完成
        yield {
            "type": "done",
            "data": {
                "total": total,
                "message": "所有项目处理完成"
            }
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "PROCESSING_ERROR"
        }
```

### 示例 2: LLM 流式输出

```python
from typing import Iterator, Dict, Any
from openai import OpenAI
import os

def chat_stream(messages: list, model: str = "gpt-4o-mini") -> Iterator[Dict[str, Any]]:
    """流式 LLM 聊天"""
    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # 开始
        yield {
            "type": "start",
            "data": {"model": model}
        }
        
        # 流式调用
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        # 逐块返回
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {
                    "type": "content",
                    "data": chunk.choices[0].delta.content
                }
        
        # 完成
        yield {
            "type": "done",
            "data": {"finish_reason": "stop"}
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "LLM_ERROR"
        }
```

### 示例 3: 文件处理流

```python
from pathlib import Path
from typing import Iterator, Dict, Any

def process_large_file(filepath: str) -> Iterator[Dict[str, Any]]:
    """逐行处理大文件"""
    try:
        path = Path(filepath)
        total_lines = sum(1 for _ in path.open())
        
        yield {
            "type": "start",
            "data": {"total_lines": total_lines}
        }
        
        processed = 0
        with path.open() as f:
            for line in f:
                # 处理行
                result = process_line(line)
                processed += 1
                
                # 每100行报告一次进度
                if processed % 100 == 0:
                    yield {
                        "type": "progress",
                        "data": {
                            "processed": processed,
                            "total": total_lines,
                            "percentage": int((processed / total_lines) * 100)
                        }
                    }
        
        yield {
            "type": "done",
            "data": {"processed": processed}
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "FILE_ERROR"
        }
```

## 客户端调用

### Python 客户端

```python
import requests
import json

response = requests.post(
    "http://factory:8000/invoke/my_stream_function",
    json={"inputs": {"param": "test"}},
    stream=True  # 重要：启用流式
)

for line in response.iter_lines():
    if line.startswith(b'data: '):
        event = json.loads(line[6:])
        
        if event["type"] == "progress":
            print(f"进度: {event['data']['percentage']}%")
        elif event["type"] == "content":
            print(event["data"], end="", flush=True)
        elif event["type"] == "done":
            print("\n完成!")
```

### JavaScript 客户端

```javascript
const response = await fetch(url, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({inputs: {param: 'test'}})
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      
      switch (event.type) {
        case 'progress':
          console.log(`进度: ${event.data.percentage}%`);
          break;
        case 'content':
          process.stdout.write(event.data);
          break;
        case 'done':
          console.log('\n完成!');
          break;
      }
    }
  }
}
```

## 最佳实践

### 1. **错误处理**

```python
def safe_stream(param: str) -> Iterator[Dict]:
    try:
        # 开始事件
        yield {"type": "start", "data": {...}}
        
        # 业务逻辑
        for item in process():
            yield {"type": "progress", "data": item}
        
        # 完成事件
        yield {"type": "done", "data": {...}}
        
    except SpecificError as e:
        # 特定错误
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "SPECIFIC_ERROR"
        }
    except Exception as e:
        # 通用错误
        yield {
            "type": "error",
            "data": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
```

### 2. **资源管理**

```python
def stream_with_resources() -> Iterator[Dict]:
    connection = None
    try:
        connection = open_connection()
        yield {"type": "start", "data": {}}
        
        # 使用资源
        for data in connection.read_stream():
            yield {"type": "progress", "data": data}
        
        yield {"type": "done", "data": {}}
        
    finally:
        # 确保资源被释放
        if connection:
            connection.close()
```

### 3. **进度频率控制**

```python
def controlled_stream(items: list) -> Iterator[Dict]:
    """避免发送过多进度事件"""
    total = len(items)
    last_percentage = -1
    
    for i, item in enumerate(items):
        result = process(item)
        
        # 只在百分比变化时报告
        percentage = int((i / total) * 100)
        if percentage != last_percentage:
            yield {"type": "progress", "data": {"percentage": percentage}}
            last_percentage = percentage
```

### 4. **测试建议**

```python
def test_stream_function():
    # 收集所有事件
    events = list(my_stream_function("test"))
    
    # 验证事件顺序
    assert events[0]["type"] == "start"
    assert events[-1]["type"] == "done"
    
    # 验证进度事件
    progress_events = [e for e in events if e["type"] == "progress"]
    assert len(progress_events) > 0
    
    # 验证数据完整性
    for event in progress_events:
        assert "data" in event
        assert event["data"]["current"] <= event["data"]["total"]
```

## 性能优化

### 1. **批量发送**

```python
def batch_yield(items: list, batch_size: int = 100) -> Iterator[Dict]:
    """批量发送减少网络开销"""
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        yield {
            "type": "progress",
            "data": {"batch": batch, "index": i}
        }
```

### 2. **缓冲控制**

```python
def buffered_stream() -> Iterator[Dict]:
    """定期刷新缓冲"""
    import sys
    
    for i in range(100):
        yield {"type": "progress", "data": {"count": i}}
        
        # 定期刷新输出缓冲
        if i % 10 == 0:
            sys.stdout.flush()
```

## 常见问题

### Q: 流式函数可以使用 async/await 吗？

A: 当前版本只支持同步生成器（`def` + `yield`），不支持异步生成器（`async def` + `yield`）。

### Q: 如何处理客户端断开连接？

A: 生成器会继续执行直到完成或出错。建议在长时间运行的循环中添加检查机制。

### Q: 流式函数可以返回文件吗？

A: 可以，按照 v3.0 文件处理规范，写入 `data/outputs/` 即可。文件 URL 会在流结束后由 Gateway 返回。

### Q: 如何测试流式函数？

A: 使用 `list()` 收集所有事件，然后验证事件顺序和数据完整性。

## 参考资源

- [LLM Client 预制件](https://github.com/your-org/llm-client) - 完整的流式 LLM 实现
- [Handler 流式支持](../prefab-factory/STREAMING_SUPPORT.md) - Handler 层实现细节
- [SSE 协议规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

**更新时间**: 2024-10-23  
**适用版本**: v3.0+

