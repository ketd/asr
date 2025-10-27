# 📚 文档索引

本项目包含完整的文档体系，帮助不同角色的用户快速上手。

## 📖 核心文档

### 入门必读

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [README.md](README.md) | 主文档，完整的使用指南 | 所有用户 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 快速参考卡片，常用命令速查 | 日常开发 |
| [prd.md](prd.md) | 产品需求文档，了解项目背景 | 架构师、PM |

### 深度学习

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计文档，技术选型、设计理念和项目结构 | 架构师、高级开发者、新贡献者 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南，代码规范和提交流程 | 贡献者 |
| [STREAMING_GUIDE.md](STREAMING_GUIDE.md) | 流式函数开发指南，实现实时输出 | 开发者 |

### 特殊用途

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [AGENTS.md](AGENTS.md) | AI 助手开发指南 | AI 编程助手 |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新日志 | 所有用户 |

## 🗂️ 配置文件

| 文件 | 说明 | 作用 |
|------|------|------|
| `pyproject.toml` | 项目配置 | 依赖管理、构建配置、工具配置 |
| `prefab-manifest.json` | 函数元数据 | AI 理解和调用函数的"契约" |
| `.editorconfig` | 编辑器配置 | 统一不同编辑器的代码风格 |
| `.flake8` | Linter 配置 | Python 代码风格检查规则 |
| `.gitignore` | Git 忽略规则 | 指定不纳入版本控制的文件 |

## 🛠️ 脚本工具

| 脚本 | 说明 | 用法 |
|------|------|------|
| `scripts/validate_manifest.py` | Manifest 验证 | `uv run python scripts/validate_manifest.py` |
| `scripts/version_bump.py` | 版本号升级 | `uv run python scripts/version_bump.py [patch\|minor\|major]` |
| `scripts/quick_start.py` | 快速验证 | `uv run python scripts/quick_start.py` |

## 📋 模板文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `.github/workflows/build-and-release.yml` | CI/CD 流程 | 自动化测试、构建、发布 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR 模板 | 规范 Pull Request 格式 |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug 报告模板 | 规范 Bug 报告格式 |
| `.github/ISSUE_TEMPLATE/feature_request.md` | 功能请求模板 | 规范功能请求格式 |

## 📚 学习路径

### 🆕 新手入门（15分钟）

1. 阅读 [README.md](README.md) 了解项目概况
2. 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 掌握常用命令
3. 运行 `uv run python scripts/quick_start.py` 验证环境

### 💼 日常开发（30分钟）

1. 熟悉 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 中的开发流程
2. 参考 [AGENTS.md](AGENTS.md) 了解开发规范
3. 查看 [src/main.py](src/main.py) 学习示例代码

### 🏗️ 架构理解（1小时）

1. 阅读 [prd.md](prd.md) 理解产品需求
2. 学习 [ARCHITECTURE.md](ARCHITECTURE.md) 掌握技术架构和实现细节

### 🤝 贡献代码（2小时）

1. 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程
2. 学习 [CODE OF CONDUCT](CONTRIBUTING.md#行为准则) 了解行为规范
3. 参考 [PULL_REQUEST_TEMPLATE](.github/PULL_REQUEST_TEMPLATE.md) 提交 PR

## 🔍 快速查找

### 我想...

- **了解项目是什么** → [README.md](README.md) 开头部分
- **快速开始开发** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **理解技术选型** → [ARCHITECTURE.md](ARCHITECTURE.md) 技术选型章节
- **添加新功能** → [CONTRIBUTING.md](CONTRIBUTING.md) 开发工作流
- **发布新版本** → [README.md](README.md#5-发布预制件) 或 [QUICK_REFERENCE.md](QUICK_REFERENCE.md#版本管理与发布)
- **查看示例代码** → [src/main.py](src/main.py)
- **实现流式函数** → [STREAMING_GUIDE.md](STREAMING_GUIDE.md)
- **修复 CI/CD 问题** → [ARCHITECTURE.md](ARCHITECTURE.md#cicd-流程)
- **配置 AI 助手** → [AGENTS.md](AGENTS.md)

### 常见问题在哪找？

- **如何添加依赖？** → [README.md](README.md#依赖管理)
- **如何编写测试？** → [CONTRIBUTING.md](CONTRIBUTING.md#测试覆盖)
- **Manifest 验证失败？** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md#manifest-验证失败)
- **如何处理敏感信息？** → [README.md](README.md#q-如何处理敏感信息如-api-key)
- **可以添加多个文件吗？** → [README.md](README.md#q-可以添加多个-py-文件吗)

## 📊 文档统计

| 类型 | 数量 | 总字数（约） |
|------|------|-------------|
| 主要文档 | 7 个 | 20,000+ |
| 配置文件 | 5 个 | - |
| 脚本工具 | 3 个 | - |
| 模板文件 | 4 个 | - |

## 🎯 推荐阅读顺序

### 按角色推荐

**🔰 初学者**
1. README.md → QUICK_REFERENCE.md → src/main.py 示例

**👨‍💻 开发者**
1. QUICK_REFERENCE.md → AGENTS.md → CONTRIBUTING.md

**🏗️ 架构师**
1. prd.md → ARCHITECTURE.md

**🤖 AI 助手**
1. AGENTS.md → ARCHITECTURE.md → 具体代码文件

### 按任务推荐

**🚀 快速上手**
1. README.md（快速开始部分）
2. QUICK_REFERENCE.md
3. 运行示例代码

**📝 编写代码**
1. AGENTS.md（开发规范）
2. src/main.py（代码示例）
3. CONTRIBUTING.md（代码风格）

**🔧 解决问题**
1. QUICK_REFERENCE.md（故障排查）
2. ARCHITECTURE.md（架构理解）
3. GitHub Issues（已知问题）

## 💡 文档维护

### 更新原则
- 代码变更必须同步更新相关文档
- 重大架构调整需要更新 ARCHITECTURE.md
- 新功能添加需要更新 CHANGELOG.md
- API 变更必须更新 AGENTS.md 和 README.md

### 文档审核
- 所有文档更新需要通过 PR 审核
- 确保示例代码可以正常运行
- 保持文档之间的一致性

---

**提示**: 如果您找不到需要的信息，请[提交 Issue](https://github.com/your-org/prefab-template/issues) 告诉我们！

