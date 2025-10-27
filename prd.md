### **产品需求文档 (PRD): AI 预制件模板仓库 (`prefab-template`)**

**版本:** 1.0
**日期:** 2025年10月14日
**负责人:** [您的名字/团队名]

#### **1. 背景与愿景 (Background & Vision)**

**1.1. 问题陈述:**
我们的 AI 编码平台在处理复杂、多步骤的业务逻辑时能力有限，生成的代码往往不可用。为了解决这一问题，我们引入了一个社区驱动的“预制件 (Prefab)”生态系统，允许开发者贡献可复用的高质量代码模块，供 AI 在明确需求后直接调用。

**1.2. 产品愿景:**
`prefab-template` 仓库是整个预制件生态的基石。它并非一个可运行的产品，而是一个标准化的“模具”或“脚手架”。任何希望为平台贡献代码的开发者都将从这个模板开始。它的成功将直接决定社区贡献的质量、一致性和可维护性，是实现整个生态系统自动化的关键。

**1.3. 核心目标:**
*   **标准化 (Standardization):** 为所有社区贡献提供一个统一、可预测的文件结构和配置规范。
*   **自动化 (Automation):** 内置强大的 CI/CD 流程，自动完成测试、验证、打包和发布，将贡献者的手动操作降至最低。
*   **降低门槛 (Accessibility):** 提供清晰的指导和示例，使不同水平的 Python 开发者都能轻松上手，专注于业务逻辑而非工程细节。
*   **质量保证 (Quality Assurance):** 通过强制性的代码检查和测试，确保所有进入生态的预制件都达到基本质量标准。

#### **2. 目标用户 (Target Audience)**

*   **社区贡献者 (Community Contributor):** 熟悉 Python 的开发者，他们希望将自己编写的实用函数或类库分享到我们的平台。他们可能不是打包或 CI/CD 专家，希望贡献过程尽可能简单直接。

#### **3. 功能性需求 (Functional Requirements)**

**FR-1: 标准化的仓库文件结构**
模板仓库必须包含以下文件和目录结构，每个都有其明确的用途：

*   `.github/workflows/build-and-release.yml`: **[核心]** GitHub Actions 配置文件，定义了所有自动化流程。
*   `src/`: **[核心]** 存放预制件核心业务逻辑的目录。
    *   `main.py`: 预制件的唯一指定入口，所有暴露给 AI 的函数必须在此文件中。
*   `tests/`: 存放单元测试的目录。
    *   `test_main.py`: `main.py` 对应的测试文件示例。
*   `.gitignore`: 标准的 Python `.gitignore` 文件，用于忽略不必要的文件。
*   `LICENSE`: 开源许可证文件，默认为 MIT License。
*   `prefab-manifest.json`: **[核心]** 预制件的元数据描述文件，是 AI 理解如何使用该预制件的“API 契约”。
*   `README.md`: **[核心]** 标准化的文档模板，用于向其他开发者解释预制件的功能和用法。
*   `requirements.txt`: **[核心]** 定义预制件运行时依赖的唯一文件。

**FR-2: `prefab-manifest.json` 规范**
该文件必须遵循严格的 JSON Schema，包含以下字段：

*   `schema_version` (string, required): 清单文件的版本号，例如 "1.0"。
*   `id` (string, required): 全局唯一的预制件 ID (e.g., "video-to-text-v1")。
*   `version` (string, required): 预制件的语义化版本号 (e.g., "1.0.0")。此版本号必须与触发构建的 Git Tag 保持一致。
*   `entry_point` (string, required, fixed): 固定值为 "src/main.py"。
*   `dependencies_file` (string, required, fixed): 固定值为 "pyproject.toml"。
*   `functions` (array, required): 描述所有可被 AI 调用的函数的列表。
    *   每个函数对象包含 `name`, `description`, `parameters` (参数列表), `returns` (返回值描述)。

**FR-3: 自动化 CI/CD 工作流 (`build-and-release.yml`)**
该工作流必须实现以下自动化步骤：

1.  **触发条件:** 当一个格式为 `v*.*.*` (e.g., `v1.0.0`) 的 Git Tag 被推送到仓库时触发。
2.  **验证阶段 (Validation):**
    *   使用 `uv run --with flake8` 运行代码风格检查 (Flake8)。
    *   使用 `uv run --with pytest` 运行单元测试 (Pytest)。
    *   **关键验证:** 运行一个脚本，校验 `prefab-manifest.json` 与 `src/main.py` 中的函数签名是否一致（包括返回值结构）。
    *   *任何验证失败都将导致整个流程失败。*
3.  **构建阶段 (Build):**
    *   创建一个临时的 `build/` 目录。
    *   将 `src/` 目录和 `prefab-manifest.json` 复制到 `build/`。
    *   从 `pyproject.toml` 读取运行时依赖，使用 `uv pip install --target=./build/vendor` 将所有依赖项下载到 `build/vendor/` 目录。
4.  **打包阶段 (Packaging):**
    *   将 `build/` 目录的内容打包成一个 `.tar.gz` 压缩文件，命名规范为 `{id}-{version}.tar.gz` (e.g., `hello-world-prefab-0.0.4.tar.gz`)。
5.  **发布阶段 (Release):**
    *   自动创建一个与 Git Tag 对应的 GitHub Release。
    *   将打包好的 `.tar.gz` 文件作为该 Release 的唯一附件 (Artifact) 上传。

**FR-4: `README.md` 文档模板**
`README.md` 必须提供一个结构化的模板，引导贡献者填写以下部分：
*   预制件名称
*   简介 (一句话描述)
*   功能特性 (列表)
*   使用示例 (手动调用代码片段)
*   AI 集成说明 (解释如何在平台内通过自然语言调用)
*   配置要求 (如需环境变量等)

**FR-5: 提供一个可工作的示例**
模板本身不能是空的，必须包含一个简单但完整的“Hello World”示例预制件，以便贡献者可以立即看到一个可以工作的最终形态，并在此基础上进行修改。

#### **4. 非功能性需求 (Non-Functional Requirements)**

*   **易用性 (Usability):** 贡献者在不阅读长篇大论的文档的情况下，仅通过模板内的注释和示例代码就应该能理解如何开始工作。
*   **可靠性 (Reliability):** CI/CD 流程必须稳定可靠，并在失败时提供清晰、可操作的错误日志。
*   **安全性 (Security):** CI/CD 环境应与外部网络隔离（除了下载依赖阶段），防止恶意脚本执行。

#### **5. 范围之外 (Out of Scope)**

*   **多语言支持:** 此模板仅支持 Python 3.11+。
*   **发布到 PyPI:** 本方案不使用公有 PyPI，分发方式完全依赖 GitHub Release。
*   **复杂的 Git 工作流:** 模板不包含除 Tag-Release 之外的复杂分支策略或开发流程。

#### **6. 成功指标 (Success Metrics)**

*   **模板采用率:** 社区创建的有效预制件中，使用此模板的比例 > 95%。
*   **CI/CD 首次成功率:** 新贡献者在三次尝试内成功触发 CI/CD 并发布第一个版本的比例 > 80%。
*   **“如何构建”的支持问题数量:** 关于打包、发布等工程问题的支持请求数量持续维持在低水平。