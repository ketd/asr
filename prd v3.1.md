# Prefab Template v3.1 - 回滚到 Hatchling 构建系统

> **版本**: 3.1  
> **日期**: 2025-10-17  
> **状态**: 实施中  
> **前置版本**: v3.0

## 背景

在 v2.2 版本中，我们将构建后端从 `hatchling` 改为 `setuptools`，目的是使用更"传统"和"稳定"的构建工具。然而，在实际使用中发现 setuptools 在现代 Python 项目中反而带来了更多的配置复杂性。

## 问题分析

### setuptools 的局限性

#### 1. 需要额外的 MANIFEST.in 配置

使用 setuptools 时，要将 `prefab-manifest.json` 打包进 wheel，需要配置：

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.setuptools.package-data]
"*" = ["*.json"]
```

这种配置方式有几个问题：
- **不直观**: 需要理解 `packages.find` 和 `package-data` 的区别
- **容易出错**: JSON 文件可能在某些边界情况下不被打包
- **维护成本高**: 每次添加新的非 Python 文件类型都需要更新配置

#### 2. 配置冗长且难以理解

setuptools 的配置语法继承自传统的 `setup.py` 时代，对于新手来说学习曲线陡峭：
- `where` 和 `include` 参数容易混淆
- `package-data` 使用通配符模式，但规则不够清晰
- 需要额外了解 setuptools 的打包机制

#### 3. 与现代工具链不兼容

- setuptools 的某些行为在不同版本间不一致
- 与 `uv` 等现代包管理器集成时偶有问题
- 社区逐渐转向更现代的构建后端

### hatchling 的优势

#### 1. 配置极简

只需一行配置就能指定要打包的内容：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**自动行为**：
- 自动包含 `src/` 目录下的所有内容（包括 Python 文件和非 Python 文件）
- 自动处理 `pyproject.toml` 和 `README.md`
- 自动生成正确的 wheel 元数据

#### 2. 符合现代标准

- 完全遵循 PEP 517 和 PEP 621 标准
- 由 PyPA（Python Packaging Authority）积极维护
- 与 `uv`、`pip`、`build` 等工具无缝集成

#### 3. 更好的开发体验

- 配置即文档：配置项一目了然
- 错误信息清晰：出问题时更容易排查
- 约定优于配置：遵循目录结构约定即可

## 解决方案

### 修改内容

#### 1. 修改 `pyproject.toml`

**之前（setuptools）**:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.setuptools.package-data]
"*" = ["*.json"]
```

**之后（hatchling）**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

# 确保 prefab-manifest.json 被包含在 wheel 包中
[tool.hatch.build.targets.wheel.force-include]
"prefab-manifest.json" = "prefab-manifest.json"
```

**减少了 3 行配置，更加清晰直观！**

**注意**：虽然 hatchling 会自动包含 `src/` 目录下的所有文件，但 `prefab-manifest.json` 位于项目根目录，因此需要用 `force-include` 显式声明。这比 setuptools 的 `package-data` 配置更直观易懂。

#### 2. 无需 MANIFEST.in

hatchling 会自动包含 `src/` 目录下的所有文件，包括：
- Python 源文件 (`.py`)
- JSON 配置文件
- 其他资源文件

对于根目录的 `prefab-manifest.json`，使用 `force-include` 显式声明即可，无需复杂的 MANIFEST.in 配置。

#### 3. 验证构建产物

确保 wheel 文件包含所有必要内容：
```bash
uv build
unzip -l dist/*.whl | grep manifest
```

## 影响范围

### 需要修改的文件
- ✅ `pyproject.toml` - 构建系统配置
- ✅ `prd v3.1.md` - 本文档

### 不受影响的部分
- ✅ CI/CD 流程 - 无需修改，`uv build` 命令保持不变
- ✅ 用户代码 - 完全向后兼容
- ✅ 发布流程 - wheel 格式完全相同

## 验证计划

### 本地验证
```bash
# 1. 清理旧的构建产物
rm -rf dist/ build/ *.egg-info/

# 2. 使用 hatchling 构建
uv build

# 3. 检查 wheel 内容
unzip -l dist/*.whl

# 4. 验证 manifest 文件被正确打包
unzip -l dist/*.whl | grep prefab-manifest.json

# 5. 安装并测试
pip install dist/*.whl
python -c "import src; print(src.__version__)"
```

### CI/CD 验证
- 推送 tag 触发自动构建
- 验证 Release 中的 wheel 文件完整性
- 确保所有测试通过

## 文档更新

### 需要更新的文档
1. **AGENTS.md** - 更新构建系统说明
2. **README.md** - 更新技术栈说明
3. **ARCHITECTURE.md** - 更新构建流程
4. **QUICK_REFERENCE.md** - 保持构建命令不变

### 更新要点
- 强调 hatchling 的简洁性
- 说明为什么选择 hatchling 而不是 setuptools
- 提供配置示例

## 迁移指南（给已有项目使用者）

如果你基于旧版本模板创建了项目，想要升级到 hatchling：

### 步骤 1: 更新 pyproject.toml
```bash
# 删除 setuptools 相关配置
# 添加 hatchling 配置（见上文）
```

### 步骤 2: 删除 MANIFEST.in（如果存在）
```bash
rm MANIFEST.in  # hatchling 不需要此文件
```

### 步骤 3: 验证构建
```bash
uv build
unzip -l dist/*.whl
```

### 步骤 4: 测试安装
```bash
pip install dist/*.whl
python -c "import src"
```

## 技术对比

| 特性 | setuptools | hatchling | 胜者 |
|-----|-----------|-----------|------|
| 配置行数 | ~9 行 | ~6 行 | ✅ hatchling |
| 自动包含非 Python 文件 | ❌ 需要配置 | ✅ 自动 | ✅ hatchling |
| 学习曲线 | 陡峭 | 平缓 | ✅ hatchling |
| 现代化 | 传统工具 | 现代工具 | ✅ hatchling |
| 社区趋势 | 稳定但老旧 | 活跃 | ✅ hatchling |
| PEP 517/621 兼容 | ✅ 部分 | ✅ 完全 | ✅ hatchling |
| 错误信息 | 模糊 | 清晰 | ✅ hatchling |
| 与 uv 集成 | ✅ 良好 | ✅ 优秀 | ✅ hatchling |

## 版本规划

- **v3.1**: 回滚到 hatchling（当前版本）
- **v3.2**: 基于 hatchling 进一步优化构建流程
- **v4.0**: 考虑支持多语言预制件（需要重新评估构建系统）

## 总结

setuptools 虽然是 Python 生态的"老兵"，但在简单项目中反而增加了不必要的复杂性。hatchling 作为现代化构建工具，提供了：

✅ **更简洁的配置** - 6 行 vs 9 行（减少 33%）  
✅ **更清晰的语义** - `force-include` 比 `package-data` 更直观  
✅ **更好的开发体验** - 配置即文档，错误信息清晰  
✅ **更强的未来兼容性** - 符合最新 Python 打包标准

对于预制件模板这样的简单项目，hatchling 是更好的选择。

## 参考资料

- [PEP 517 - A build-system independent format for source trees](https://peps.python.org/pep-0517/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/config/build/)
- [Why I switched from setuptools to hatchling](https://drivendata.co/blog/python-packaging-2023)

---

**变更类型**: 优化  
**破坏性变更**: 否  
**升级建议**: 推荐升级，但不强制

