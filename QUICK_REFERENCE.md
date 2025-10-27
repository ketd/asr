# 快速参考卡片

## 🚀 一分钟快速开始

```bash
# 1. 克隆仓库（或使用模板创建）
git clone https://github.com/your-org/prefab-template.git my-prefab
cd my-prefab

# 2. 安装 uv（如果还没安装）
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 安装依赖（自动创建虚拟环境）
uv sync --dev

# 4. 运行快速验证（可选但推荐）
uv run python scripts/quick_start.py

# 5. 开始编码！
# 编辑 src/main.py 和 prefab-manifest.json
```

## 📝 核心文件

| 文件 | 作用 | 必须修改 |
|------|------|----------|
| `src/main.py` | 核心业务逻辑 | ✅ 是 |
| `prefab-manifest.json` | 函数元数据描述 | ✅ 是 |
| `tests/test_main.py` | 单元测试 | ✅ 是 |
| `pyproject.toml` | 项目配置和依赖 | 如需依赖 |
| `README.md` | 项目文档 | 建议修改 |

## 🔨 常用命令

```bash
# 依赖管理
uv add requests                            # 添加运行时依赖
uv add --dev pytest                        # 添加开发依赖
uv sync --dev                              # 同步所有依赖

# 测试
uv run pytest tests/ -v                    # 运行单元测试
uv run pytest tests/ -v --cov=src          # 测试 + 覆盖率

# 代码检查
uv run flake8 src/ --max-line-length=120   # 代码风格
uv run python scripts/validate_manifest.py # Manifest验证

# 一键验证（推荐）
uv run python scripts/quick_start.py       # 运行所有检查

# 版本管理与发布
uv run python scripts/version_bump.py patch  # 升级补丁版本
uv run python scripts/version_bump.py minor  # 升级次版本
uv run python scripts/version_bump.py major  # 升级主版本
git tag v1.0.0 && git push origin v1.0.0     # 推送发布
```

## 📦 发布检查清单

发布前确保：

- [ ] `src/main.py` 已编写业务逻辑
- [ ] `prefab-manifest.json` 版本号已更新
- [ ] 所有测试通过 (`uv run pytest tests/ -v`)
- [ ] 代码风格检查通过 (`uv run flake8 src/`)
- [ ] Manifest 验证通过 (`uv run python scripts/validate_manifest.py`)
- [ ] `README.md` 已更新说明
- [ ] Tag 版本号与 manifest 一致

## 🎯 函数编写模板

```python
def your_function(param1: str, param2: int = 0) -> dict:
    """
    一句话描述函数功能
    
    Args:
        param1: 参数1说明
        param2: 参数2说明（可选，默认0）
    
    Returns:
        返回值说明
    """
    try:
        # 业务逻辑
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## 📋 Manifest 模板

```json
{
  "name": "function_name",
  "description": "函数功能描述",
  "parameters": [
    {
      "name": "param1",
      "type": "string",
      "description": "参数说明",
      "required": true
    },
    {
      "name": "param2",
      "type": "integer",
      "description": "参数说明",
      "required": false,
      "default": 0
    }
  ],
  "returns": {
    "type": "object",
    "description": "返回 {success: bool, result: any} 或 {success: bool, error: str}"
  }
}
```

**类型系统 (v2.2):**
- 基础类型: `string`, `number`, `integer`, `boolean`, `object`, `array`
- 平台类型: `InputFile`（输入文件）, `OutputFile`（输出文件）

## 🐛 故障排查

### Manifest 验证失败

```bash
# 运行验证看详细错误
uv run python scripts/validate_manifest.py

# 常见问题：
# - 函数名不匹配 → 检查拼写
# - 参数不匹配 → 检查参数名和required属性
# - JSON格式错误 → 使用JSON验证工具
```

### 测试失败

```bash
# 查看详细输出
uv run pytest tests/ -v -s

# 只运行特定测试
uv run pytest tests/test_main.py::TestAnalyzeDataset::test_statistics_operation -v
```

### CI/CD 未触发

```bash
# 检查Tag格式（必须是 v*.*.*）
git tag -l                    # 列出所有tag
git tag -d v1.0.0            # 删除错误tag
git push origin :refs/tags/v1.0.0  # 删除远程tag

# 正确创建tag
git tag v1.0.0
git push origin v1.0.0
```

## 📊 版本号规范

遵循语义化版本 (Semantic Versioning):

```
v主版本.次版本.修订号
v1.0.0

主版本：不兼容的API更改
次版本：向后兼容的功能新增
修订号：向后兼容的问题修复

示例：
v1.0.0 → v1.0.1  # Bug修复（patch）
v1.0.1 → v1.1.0  # 新功能（minor）
v1.1.0 → v2.0.0  # 破坏性更改（major）
```

**使用版本升级脚本：**
```bash
# 自动更新 prefab-manifest.json 和 pyproject.toml
uv run python scripts/version_bump.py patch
# 然后按提示操作即可
```

## 🔗 重要链接

- [完整文档](README.md) - 详细的使用指南
- [贡献指南](CONTRIBUTING.md) - 如何贡献代码
- [架构设计](ARCHITECTURE.md) - 架构、设计理念和项目结构
- [文档索引](DOCS_INDEX.md) - 所有文档导航

## 💡 最佳实践

1. **函数设计**
   - ✅ 使用类型提示
   - ✅ 返回结构化数据（字典）
   - ✅ 包含错误处理
   - ✅ 单一职责原则

2. **测试覆盖**
   - ✅ 测试正常情况
   - ✅ 测试边界情况
   - ✅ 测试错误处理

3. **文档编写**
   - ✅ 清晰的函数文档字符串
   - ✅ README包含使用示例
   - ✅ 说明配置要求（如环境变量）

4. **依赖管理**
   - ✅ 锁定版本号（如 `requests>=2.31.0`）
   - ✅ 只添加必要的依赖
   - ✅ 测试依赖单独标注

## 🎁 示例代码片段

### 带配置的函数

```python
def fetch_data(url: str, api_key: str = None) -> dict:
    """
    从API获取数据
    
    Args:
        url: API地址
        api_key: API密钥（可选，可从环境变量获取）
    """
    import os
    import requests
    
    key = api_key or os.getenv('API_KEY')
    if not key:
        return {"success": False, "error": "API key required"}
    
    response = requests.get(url, headers={'Authorization': f'Bearer {key}'})
    
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "error": response.text}
```

### 异步函数处理

```python
def process_batch(items: list, batch_size: int = 10) -> dict:
    """批量处理数据"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        # 处理批次
        batch_result = process(batch)
        results.extend(batch_result)
    
    return {
        "success": True,
        "processed": len(results),
        "results": results
    }
```

---

**保存此文件为书签，随时查阅！📌**

