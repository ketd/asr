# AI 预制件开发指南

> 本指南将教你如何创建标准化的 AI 预制件（Prefab），使其能够被 AI 直接调用。

## 📚 目录

- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [函数编写规范](#函数编写规范)
- [Manifest 编写规范](#manifest-编写规范)
- [依赖管理](#依赖管理)
- [测试与验证](#测试与验证)
- [部署流程](#部署流程)
- [常见问题](#常见问题)

---

## 快速开始

### 1. 环境准备

```bash
# 安装 uv（Python 包管理器）
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 同步依赖
uv sync --dev
```

### 2. 编写你的第一个函数

在 `src/main.py` 中编写函数：

```python
def greet(name: str = "World") -> dict:
    """
    向用户问候
    
    Args:
        name: 要问候的名字
    
    Returns:
        包含问候语的字典
    """
    try:
        message = f"Hello, {name}!"
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 3. 在 Manifest 中注册函数

在 `prefab-manifest.json` 中添加函数描述：

```json
{
  "functions": [
    {
      "name": "greet",
      "description": "向用户问候",
      "parameters": [
        {
          "name": "name",
          "type": "string",
          "description": "要问候的名字",
          "required": false,
          "default": "World"
        }
      ],
      "returns": {
        "type": "object",
        "description": "包含问候结果的对象"
      }
    }
  ]
}
```

### 4. 测试函数

```bash
# 运行测试
uv run pytest tests/ -v

# 验证 manifest
uv run python scripts/validate_manifest.py
```

---

## 核心概念

### 什么是预制件（Prefab）？

预制件是一个**标准化的 Python 模块**，它：
- 包含可被 AI 直接调用的函数
- 有明确的函数签名和返回值
- 通过 `prefab-manifest.json` 描述其能力
- 可以自动打包、部署和调用

### 文件结构

```
prefab-template/
├── src/                      # 源代码
│   ├── __init__.py          # 模块导出
│   ├── main.py              # 主入口（必须）
│   └── utils/               # 工具模块（可选）
├── tests/                   # 测试文件
├── prefab-manifest.json     # 函数元数据（核心）
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

---

## 函数编写规范

### ✅ 必须遵守的规则

#### 1. 所有函数必须在 `src/main.py` 中定义

```python
# ✅ 正确：在 main.py 中定义
def my_function(arg1: str) -> dict:
    pass

# ❌ 错误：在其他文件中定义暴露给 AI 的函数
# src/other.py
def my_function(arg1: str) -> dict:
    pass
```

#### 2. 函数必须有类型提示

```python
# ✅ 正确：完整的类型提示
def process_text(text: str, max_length: int = 100) -> dict:
    pass

# ❌ 错误：缺少类型提示
def process_text(text, max_length=100):
    pass
```

#### 3. 函数必须有 Docstring

```python
def my_function(param: str) -> dict:
    """
    一句话描述函数功能
    
    Args:
        param: 参数说明
    
    Returns:
        返回值说明
    """
    pass
```

#### 4. 返回值必须是字典，包含 `success` 字段

```python
# ✅ 推荐：结构化返回值
def my_function(param: str) -> dict:
    try:
        result = do_something(param)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "OPERATION_FAILED"
        }

# ⚠️ 可接受：简单返回值（但不推荐）
def my_function(param: str) -> dict:
    return {"result": "ok"}
```

### 📝 函数设计最佳实践

#### 1. 错误处理

```python
def safe_divide(a: float, b: float) -> dict:
    """安全的除法运算"""
    try:
        if b == 0:
            return {
                "success": False,
                "error": "除数不能为零",
                "error_code": "DIVISION_BY_ZERO"
            }
        
        result = a / b
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
```

#### 2. 参数验证

```python
def process_list(items: list, min_count: int = 1) -> dict:
    """处理列表"""
    # 参数验证
    if not isinstance(items, list):
        return {
            "success": False,
            "error": "items 必须是列表类型",
            "error_code": "INVALID_TYPE"
        }
    
    if len(items) < min_count:
        return {
            "success": False,
            "error": f"列表至少需要 {min_count} 个元素",
            "error_code": "INSUFFICIENT_ITEMS"
        }
    
    # 处理逻辑
    result = [item.upper() for item in items]
    return {
        "success": True,
        "processed_items": result,
        "count": len(result)
    }
```

#### 3. 文件处理

```python
def read_file_content(file_path: str) -> dict:
    """读取文件内容
    
    Args:
        file_path: 文件路径（支持 InputFile 类型）
    
    Returns:
        包含文件内容的字典
    """
    try:
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"文件不存在: {file_path}",
                "error_code": "FILE_NOT_FOUND"
            }
        
        content = path.read_text(encoding='utf-8')
        return {
            "success": True,
            "content": content,
            "size": len(content),
            "path": str(path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "READ_ERROR"
        }
```

---

## Manifest 编写规范

### 基本结构

```json
{
  "schema_version": "1.0",
  "id": "your-prefab-id",
  "version": "1.0.0",
  "name": "预制件名称",
  "description": "预制件功能描述",
  "tags": ["tag1", "tag2"],
  "entry_point": "src/main.py",
  "dependencies_file": "pyproject.toml",
  "functions": [
    {
      "name": "function_name",
      "description": "函数描述",
      "parameters": [...],
      "returns": {...}
    }
  ],
  "execution_environment": {
    "cpu": "500m",
    "memory": "256Mi"
  }
}
```

### 字段说明

#### 基本信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `schema_version` | string | ✅ | Manifest 版本（固定为 "1.0"） |
| `id` | string | ✅ | 预制件唯一标识（小写字母、数字、连字符） |
| `version` | string | ✅ | 语义化版本号（如 "1.2.3"） |
| `name` | string | ✅ | 预制件显示名称 |
| `description` | string | ✅ | 功能描述（一句话说明） |
| `tags` | array | ⚠️ | 标签列表（便于搜索） |
| `entry_point` | string | ✅ | 入口文件（固定为 "src/main.py"） |
| `dependencies_file` | string | ✅ | 依赖文件（固定为 "pyproject.toml"） |

#### 函数定义

```json
{
  "name": "greet",
  "description": "向用户问候",
  "parameters": [
    {
      "name": "name",
      "type": "string",
      "description": "要问候的名字",
      "required": false,
      "default": "World"
    }
  ],
  "returns": {
    "type": "object",
    "description": "包含问候结果的对象",
    "properties": {
      "success": {
        "type": "boolean",
        "description": "操作是否成功"
      },
      "message": {
        "type": "string",
        "description": "问候消息",
        "optional": true
      },
      "error": {
        "type": "string",
        "description": "错误信息",
        "optional": true
      }
    }
  }
}
```

### 参数类型

#### 基本类型

| JSON Schema 类型 | Python 类型 | 示例 |
|-----------------|------------|------|
| `string` | `str` | `"hello"` |
| `number` | `float` | `3.14` |
| `integer` | `int` | `42` |
| `boolean` | `bool` | `true` |
| `array` | `list` | `[1, 2, 3]` |
| `object` | `dict` | `{"key": "value"}` |

#### 平台特殊类型

| 类型 | 说明 | Python 参数类型 |
|------|------|----------------|
| `InputFile` | 输入文件路径 | `str` |
| `OutputFile` | 输出文件路径 | `str` |

```json
{
  "name": "convert_file",
  "parameters": [
    {
      "name": "input_file",
      "type": "InputFile",
      "description": "输入文件路径",
      "required": true
    },
    {
      "name": "output_file",
      "type": "OutputFile",
      "description": "输出文件路径",
      "required": false
    }
  ]
}
```

### 返回值定义

#### 简单返回值

```json
{
  "returns": {
    "type": "object",
    "description": "操作结果"
  }
}
```

#### 详细返回值（推荐）

```json
{
  "returns": {
    "type": "object",
    "description": "操作结果对象",
    "properties": {
      "success": {
        "type": "boolean",
        "description": "操作是否成功"
      },
      "data": {
        "type": "object",
        "description": "成功时的数据",
        "optional": true
      },
      "error": {
        "type": "string",
        "description": "错误信息",
        "optional": true
      }
    }
  }
}
```

### 输出文件声明

如果函数返回文件路径，使用 `primary_output` 指定：

```json
{
  "name": "generate_report",
  "description": "生成报告文件",
  "primary_output": "data.output_file",
  "returns": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "data": {
        "type": "object",
        "properties": {
          "output_file": {
            "type": "OutputFile",
            "description": "报告文件路径"
          }
        }
      }
    }
  }
}
```

---

## 依赖管理

### 在 `pyproject.toml` 中声明依赖

```toml
[project]
name = "your-prefab"
version = "1.0.0"
dependencies = [
    "requests>=2.31.0",  # 必须指定版本约束
    "pandas>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",     # 开发依赖不会被打包
    "flake8>=6.1.0",
]
```

### 依赖选择建议

#### ✅ 推荐的轻量依赖

| 功能 | 推荐库 | 大小 |
|------|--------|------|
| HTTP 请求 | `httpx` | ~1MB |
| JSON 处理 | 内置 `json` | 0 |
| 日期时间 | 内置 `datetime` | 0 |
| 文件操作 | 内置 `pathlib` | 0 |
| 文本处理 | 内置 `re` | 0 |

#### ⚠️ 谨慎使用的大依赖

| 库 | 大小 | 替代方案 |
|-----|------|---------|
| `numpy` | ~100MB | 考虑是否真的需要 |
| `pandas` | ~50MB | 用 `csv` 模块 |
| `matplotlib` | ~40MB | 返回数据，让前端绘图 |
| `opencv` | ~50MB | 考虑轻量图像库 |

### 版本约束规范

```toml
dependencies = [
    "package>=1.0.0",      # ✅ 推荐：兼容性版本
    "package>=1.0.0,<2.0", # ✅ 推荐：限制大版本
    "package==1.2.3",      # ⚠️ 谨慎：固定版本
    "package",             # ❌ 禁止：无版本约束
]
```

---

## 测试与验证

### 编写测试

在 `tests/test_main.py` 中：

```python
import pytest
from src.main import greet

def test_greet_default():
    """测试默认问候"""
    result = greet()
    assert result["success"] is True
    assert "Hello, World!" in result["message"]

def test_greet_with_name():
    """测试自定义名字"""
    result = greet(name="Alice")
    assert result["success"] is True
    assert "Hello, Alice!" in result["message"]

def test_greet_error_handling():
    """测试错误处理"""
    result = greet(name=None)
    assert result["success"] is False
    assert "error" in result
```

### 运行验证

```bash
# 1. 运行所有测试
uv run pytest tests/ -v

# 2. 验证 manifest 一致性
uv run python scripts/validate_manifest.py

# 3. 代码风格检查
uv run flake8 src/ --max-line-length=120

# 4. 快速验证（一键）
uv run python scripts/quick_start.py
```

---

## 部署流程

### 1. 更新版本号

在 `prefab-manifest.json` 和 `pyproject.toml` 中同步更新版本号：

```json
// prefab-manifest.json
{
  "version": "1.0.0"
}
```

```toml
# pyproject.toml
[project]
version = "1.0.0"
```

### 2. 提交代码

```bash
git add .
git commit -m "Release v1.0.0"
```

### 3. 创建 Tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 4. 自动构建

GitHub Actions 会自动：
1. ✅ 运行测试
2. ✅ 验证 manifest
3. ✅ 构建 `.whl` 包
4. ✅ 发布到 GitHub Releases

### 5. 自动部署

当 `.whl` 包发布后：
1. ✅ 自动触发部署
2. ✅ 构建 Docker 镜像
3. ✅ 部署到 Knative
4. ✅ 生成服务 URL

---

## 常见问题

### Q1: 可以在 `src/main.py` 之外定义函数吗？

**A:** 可以创建辅助模块，但**暴露给 AI 的函数必须在 `src/main.py` 中**。

```python
# ✅ 正确的做法
# src/utils/helper.py
def internal_helper(x):
    return x * 2

# src/main.py
from .utils.helper import internal_helper

def my_function(x: int) -> dict:  # ← 暴露给 AI
    result = internal_helper(x)
    return {"success": True, "result": result}
```

### Q2: 如何处理敏感信息（API Key 等）？

**A:** 通过函数参数传递，不要硬编码。

```python
# ✅ 正确：通过参数传递
def call_api(api_key: str, endpoint: str) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    # ...

# ❌ 错误：硬编码
def call_api():
    api_key = "sk-xxx"  # 不要这样做！
```

### Q3: 函数可以返回其他类型吗（如 str, int）？

**A:** 可以，但**强烈建议返回字典**，便于统一处理。

```python
# ✅ 推荐：结构化返回值
def calculate(x: int) -> dict:
    return {
        "success": True,
        "result": x * 2
    }

# ⚠️ 可接受但不推荐
def calculate(x: int) -> int:
    return x * 2  # 无法表示错误状态
```

### Q4: Manifest 和代码不一致会怎样？

**A:** 验证脚本会报错，CI/CD 会失败。

```bash
# 运行验证
uv run python scripts/validate_manifest.py

# 如果不一致，会看到：
❌ 函数 'my_func' 在 manifest 中定义但在代码中不存在
❌ 参数 'param1' 类型不匹配：代码中是 str，manifest 中是 int
```

### Q5: 如何调试部署失败？

**A:** 查看构建日志和部署日志。

```bash
# 本地测试构建
uv run pytest tests/ -v
uv run python scripts/validate_manifest.py

# 查看 GitHub Actions 日志
# 1. 进入仓库 → Actions 标签页
# 2. 点击失败的 workflow
# 3. 查看具体错误信息
```

---

## 完整示例

### `src/main.py`

```python
"""
示例预制件：文本处理工具
"""

def to_uppercase(text: str) -> dict:
    """
    将文本转换为大写
    
    Args:
        text: 要转换的文本
    
    Returns:
        包含转换结果的字典
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "文本不能为空",
                "error_code": "EMPTY_TEXT"
            }
        
        result = text.upper()
        return {
            "success": True,
            "original": text,
            "result": result,
            "length": len(result)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def count_words(text: str) -> dict:
    """
    统计文本中的单词数量
    
    Args:
        text: 要统计的文本
    
    Returns:
        包含统计结果的字典
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "文本不能为空",
                "error_code": "EMPTY_TEXT"
            }
        
        words = text.split()
        return {
            "success": True,
            "text": text,
            "word_count": len(words),
            "char_count": len(text)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
```

### `prefab-manifest.json`

```json
{
  "schema_version": "1.0",
  "id": "text-processor",
  "version": "1.0.0",
  "name": "文本处理工具",
  "description": "提供文本转换和统计功能",
  "tags": ["text", "utility"],
  "entry_point": "src/main.py",
  "dependencies_file": "pyproject.toml",
  "functions": [
    {
      "name": "to_uppercase",
      "description": "将文本转换为大写",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "要转换的文本",
          "required": true
        }
      ],
      "returns": {
        "type": "object",
        "description": "转换结果对象",
        "properties": {
          "success": {"type": "boolean"},
          "original": {"type": "string", "optional": true},
          "result": {"type": "string", "optional": true},
          "length": {"type": "integer", "optional": true},
          "error": {"type": "string", "optional": true}
        }
      }
    },
    {
      "name": "count_words",
      "description": "统计文本中的单词数量",
      "parameters": [
        {
          "name": "text",
          "type": "string",
          "description": "要统计的文本",
          "required": true
        }
      ],
      "returns": {
        "type": "object",
        "description": "统计结果对象",
        "properties": {
          "success": {"type": "boolean"},
          "text": {"type": "string", "optional": true},
          "word_count": {"type": "integer", "optional": true},
          "char_count": {"type": "integer", "optional": true},
          "error": {"type": "string", "optional": true}
        }
      }
    }
  ],
  "execution_environment": {
    "cpu": "500m",
    "memory": "256Mi"
  }
}
```

---

## 📖 更多资源

- [项目 README](README.md) - 项目概述
- [快速参考](QUICK_REFERENCE.md) - 常用命令
- [贡献指南](CONTRIBUTING.md) - 如何贡献
- [AGENTS.md](AGENTS.md) - AI 助手指南

---

## 🆘 获取帮助

如果遇到问题：
1. 查看本指南的常见问题部分
2. 运行验证脚本查看详细错误
3. 查看 GitHub Issues
4. 提交新的 Issue

祝开发顺利！🎉

