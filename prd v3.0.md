### **产品需求文档 (PRD): AI 预制件模板仓库 (`prefab-template`)**

**版本:** 3.0 (最终稳定版)
**日期:** 2025年10月16日
**负责人:** [您的名字/团队名]

#### **变更日志 (v3.0)**
*   **架构固化:** 正式确立 `pyproject.toml` (负责打包) + `prefab-manifest.json` (负责契约) 的双文件核心模式。
*   **DevEx 优化:** 废弃 `prefab-devkit` 的概念，回归到一个纯粹、简单、无额外工具依赖的模板。
*   **安全增强:** 引入了完整的作用域化密钥管理规范，对 `prefab-manifest.json` 中的 `secrets` 字段进行了详细定义，要求提供清晰的获取指南。

---
*(背景、愿景、目标用户部分省略)*
---

#### **3. 功能性需求 (FR)**

**FR-1: 标准化的仓库文件结构**
*   `.github/workflows/build-and-release.yml`: GitHub Actions 配置文件。
*   `src/`: 存放预制件核心业务逻辑的目录 (e.g., `main.py`)。
*   `tests/`: 存放单元测试的目录。
*   **`pyproject.toml`**: **[核心]** 负责 Python 打包、依赖管理。
*   **`prefab-manifest.json`**: **[核心]** 负责定义预制件的全部元数据和“API 契约”。
*   `README.md`, `LICENSE`, `.gitignore`: 标准项目文件。

**FR-2: 配置文件规范**

**A) `pyproject.toml` (职责：Python 打包)**
此文件应保持标准和简洁。

**示例 `pyproject.toml`:**
```toml
[project]
name = "prefab-weather-api"
version = "1.0.0" # 必须与 manifest 中的版本一致
requires-python = ">=3.11"
dependencies = [
    "requests==2.31.0"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

# 关键：确保 manifest.json 被打包进 wheel 文件中
[tool.setuptools.package-data]
"*" = ["*.json"]
```

**B) `prefab-manifest.json` (职责：预制件契约)**
这是预制件的灵魂，定义了它的一切。

**示例 `prefab-manifest.json` for `weather-api-v1`:**
```json
{
  "id": "weather-api-v1",
  "version": "1.0.0",
  "name": "天气查询工具",
  "description": "通过第三方天气服务，查询指定城市的实时天气信息。",
  "tags": ["weather", "location", "api"],
  "functions": [
    {
      "name": "get_current_weather",
      "description": "获取指定城市的当前天气情况。",
      "parameters": [
        {
          "name": "city",
          "description": "需要查询的城市名称，例如 '北京'。",
          "type": "string",
          "required": true
        }
      ],
      "returns": {
        "type": "object",
        "properties": {
          "temperature": { "type": "number", "description": "摄氏温度" },
          "condition": { "type": "string", "description": "天气状况, e.g., '晴天'" }
        }
      },
      "secrets": [
        {
          "name": "API_KEY",
          "description": "用于认证的 API 密钥。",
          "instructions": "请访问 https://www.weather-provider.com/api-keys 获取您的免费 API Key。",
          "required": true
        }
      ]
    }
  ],
  "execution_environment": {
    "cpu": "0.5",
    "memory": "256Mi"
  }
}
```

**FR-3: `secrets` 字段详细规范 (全新核心)**
`functions[].secrets` 数组中的每个对象，用于声明该函数运行时所需的安全凭证。

*   **`name` (string, required):**
    *   **描述:** 密钥的名称。这将作为平台 UI 中显示的标签，以及注入到运行时的环境变量名。
    *   **规范:** 必须是大写字母、数字和下划线 (`[A-Z0-9_]+`)，例如 `API_KEY`, `DATABASE_URL`。
*   **`description` (string, required):**
    *   **描述:** 对这个密钥用途的简短、清晰的描述。会显示在平台 UI 中，帮助用户理解它是什么。
    *   **示例:** "用于连接生产 PostgreSQL 数据库的连接字符串。"
*   **`instructions` (string, optional):**
    *   **描述:** 一个**强烈推荐**的字段，为最终用户提供如何获取此密钥的明确指导。
    *   **作用:** 它将作为帮助文本显示在平台 UI 的密钥配置表单中。
    *   **示例 (包含 URL):** `"请访问 https://developer.third-party.com/keys 获取您的 API Key。"`
    *   **示例 (不含 URL):** `"请联系您的数据库管理员获取只读用户的连接凭证。"`
*   **`required` (boolean, required):**
    *   **描述:** `true` 表示此密钥是函数运行的必要条件。如果用户未在平台 UI 中配置此密钥，`prefab-gateway` 将拒绝执行该函数。

**FR-4: 类型系统规范**
*(继承自 v2.2 版本，包含 `string`, `number`, `boolean`, `object`, `array`, `InputFile`, `OutputFile` 的定义)*

**FR-5: 自动化 CI/CD 工作流 (`build-and-release.yml`)**
1.  **触发:** 在 `v*.*.*` Git Tag 上触发。
2.  **验证:**
    *   **一致性检查:** 校验 `pyproject.toml` 和 `prefab-manifest.json` 中的 `version` 字段是否完全匹配。
    *   安装 `dev` 依赖并运行 `pytest` 和 `flake8`。
3.  **构建:** 运行 `python -m build --wheel`。
4.  **发布:** 创建 GitHub Release 并上传 `.whl` 文件。

**FR-6: Manifest 编辑器 (辅助工具)**
*   **状态:** **已规划，但优先级低**。第一阶段，贡献者将手动编辑 `prefab-manifest.json`。
*   **愿景:** 未来提供一个静态 HTML 页面，通过表单和实时校验来帮助开发者生成此文件。

---
*(NFRs, Scope, Metrics 部分省略)*
---

