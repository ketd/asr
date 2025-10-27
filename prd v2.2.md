### **产品需求文档 (PRD): AI 预制件模板仓库 (`prefab-template`)**

**版本:** 2.2 (最终版)
**日期:** 2025年10月15日
**负责人:** [您的名字/团队名]

#### **变更日志 (v2.2)**
*   **新增核心规范:** 增加了全新的 **`FR-3: 类型系统规范`** 章节，详细定义了所有在 `prefab-manifest.json` 中支持的数据类型，特别是平台感知的 `InputFile` 和 `OutputFile` 抽象类型。
*   **章节重排:** 对后续章节进行了重新编号，以保证文档结构的逻辑性。

---
*(背景、愿景、目标用户、FR-1、FR-2 省略，保持 v2.1 版本不变)*
---

**FR-3: 类型系统规范 (全新核心章节)**

`prefab-manifest.json` 中的 `type` 字段是定义函数契约的核心。它遵循 JSON Schema 的基本类型，并扩展了两个平台感知的语义类型以处理文件 I/O。

**3.1 基础数据类型**
这些类型直接映射到 Python 的标准数据类型，平台负责进行类型校验。

| Manifest `type` | Python `type` in `main.py` | 描述 |
| :--- | :--- | :--- |
| `string` | `str` | 文本字符串。可配合 `enum` 字段来限定取值范围。 |
| `number` | `int` 或 `float` | 任意数字，包括整数和浮点数。 |
| `integer` | `int` | 仅限整数。 |
| `boolean` | `bool` | `true` 或 `false`。 |
| `object` | `dict` | 结构化的键值对。需通过 `properties` 字段定义其内部结构。 |
| `array` | `list` | 有序的值列表。 |

**3.2 平台感知语义类型 (Platform-Aware Semantic Types)**
这两种类型是整个文件处理基建的核心。它们为贡献者提供了完美的“本地开发假象”，而平台则在幕后处理所有复杂的文件流转。

**A) `InputFile`**
*   **用途:** 在 `parameters` 数组中，用于标记一个需要由平台从云存储下载到执行环境的**输入文件**。
*   **Manifest 语法:**
    ```json
    {
      "name": "input_video",
      "description": "需要处理的输入视频文件。",
      "type": "InputFile",
      "required": true
    }
    ```
*   **在 `main.py` 中的实现:**
    *   对应的函数参数**就是一个 `str` 类型的本地文件路径**。
    *   平台承诺，在调用函数前，会自动将用户提供的文件句柄解析、下载，并将沙箱内的一个**真实、可读的本地文件路径**作为字符串传入该参数。
    *   **示例:**
        ```python
        # def video_to_audio(input_video: str, ...):
        #     # 'input_video' 在这里就是一个像 '/workspace/some-uuid.mp4' 的路径
        #     if os.path.exists(input_video):
        #         ...
        ```

**B) `OutputFile`**
*   **用途:** 在 `returns` 对象中，用于标记一个由函数生成，并需要由平台捕获、上传回云存储的**输出文件**。
*   **Manifest 语法:**
    ```json
    "output_file": {
      "type": "OutputFile",
      "description": "输出音频文件的引用。"
    }
    ```
*   **在 `main.py` 中的实现:**
    *   函数的返回值（通常是一个字典）中，对应此字段的值**就是一个 `str` 类型的、函数写入结果的本地文件路径**。
    *   平台承诺，在函数成功返回后，会自动截获这个路径，将该文件上传至云存储，生成一个新的文件句柄，并用这个**新句柄**替换掉原始路径，最后才将这个处理过的结果返回给最终用户。
    *   **示例:**
        ```python
        # def video_to_audio(...):
        #     output_path = "/workspace/result.mp3"
        #     # ... ffmpeg 在这里生成了文件 ...
        #     return {
        #         "success": True,
        #         "data": {
        #             "output_file": output_path # <-- 返回的是沙箱内的本地路径
        #         }
        #     }
        ```

**FR-4: Manifest 编辑器 (原 FR-3)**
*   [ ] **任务:** 开发一个独立的、客户端渲染的静态 HTML 页面。
*   **功能:**
    *   提供一个可视化的表单界面，引导开发者填写 `prefab-manifest.json` 的所有字段。
    *   **内置类型系统支持:** 编辑器中的 `type` 字段应提供一个下拉菜单，包含所有已定义的**基础数据类型**和**平台感知语义类型**，并提供相应的说明。
    *   ... (其他功能保持不变)

**FR-5: 自动化 CI/CD 工作流 (`build-and-release.yml`) (原 FR-4)**
1.  **触发条件:** 在 `v*.*.*` Git Tag 上触发。
2.  **验证阶段:**
    *   校验 `pyproject.toml` 和 `prefab-manifest.json` 的格式。
    *   **关键类型校验:** CI/CD 必须校验 `prefab-manifest.json` 中使用的 `type` 都是本规范 (`FR-3`) 中已定义的类型。
    *   ... (其他验证保持不变)
3.  **构建与发布阶段:** (保持不变)

*(后续章节 FR-6 等顺延)*

---
**结论**

这份 v2.2 版本的 PRD 现在包含了对类型系统的完整、明确的定义。它清晰地划分了基础类型和平台感知类型，并精确描述了后者在 Manifest 声明和 Python 实现之间的“翻译”关系。这为后续的平台开发、AI prompt 设计以及社区文档撰写提供了坚实、无歧义的依据。
