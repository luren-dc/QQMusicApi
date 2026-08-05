# AGENTS.md

## Dev environment

* Python：`>=3.10`
* 依赖管理：`uv`
* 构建后端：`hatchling`

### Setup commands

* 安装依赖：`uv sync`
* 运行 Python 测试：`uv run pytest`
* 运行 Ruff 检查：`uv run ruff check qqmusic_api tests`
* 运行 Pyrefly 检查：`uv run pyrefly check`
* 运行 Docs 构建：`uv run zensical build`
* 本地预提交检查：`uv run prek run --all-files`

## Commit messages

* 使用 Conventional Commits：`<type>(<scope>): <subject>`。
* 提交信息使用中文。
* commit-msg 钩子会校验 Commitizen / Conventional Gitmoji 格式。：

## Testing rules

* **双重视角测试**：测试按层级分为 Modules 与 Core 两类视角，均以黑盒方式覆盖可观察行为：
    * **Modules 层（集成测试）**：测试重心，视为黑盒，采用基于数据驱动（`@pytest.mark.parametrize`）的函数式测试方法，将输入参数与期望结果的特征断言解耦。
    * **Core 层（单元测试）**：必要的核心逻辑测试，覆盖请求分组、批量合并、参数拼装、异常转换、分页推进等纯逻辑，不发起任何网络请求，保证测试确定性与快速性。
* **Modules 层真实网络请求（No Mock）**：禁止 Mock 底层网络请求或核心组装逻辑。必须直接与真实的 QQ 音乐 API 交互，以验证接口连通性、参数拼装和数据模型（Models）解析的正确性。
* **Core 层桩数据（Stub Only）**：仅允许使用自定义桩（如 `DummyResponse`、`MockClient`）驱动被测逻辑，禁止 Mock 被测对象自身的内部行为；不得依赖真实网络。
* **优雅处理限流（Rate Limit）**：由于 Modules 层采用真实网络请求，当触发上游 API 的风控或频率限制异常时，必须使用自定义装饰器捕获该异常并调用 `pytest.skip()` 安全跳过，严禁因此导致测试失败。
* **平铺函数写法**：摒弃测试类（`class TestXXX`），强制采用平铺的独立纯函数（Flat Functions）编写测试用例，通过 fixtures 注入依赖，保证测试的独立性。
* 测试用例必须包含单行中文 docstring，且 docstring 内部必须使用英文标点符号。
* 优先在现有的测试文件中添加用例，仅在测试全新模块时才允许创建新的测试文件。

## Documentation rules

### Python

* Docstrings 使用 Google Style。
* public API、class、方法、函数必须有 docstring。
* 测试函数必须包含单行中文 docstring（英文标点）。
* `Args` / `Returns` / `Yields` / `Raises` 按需提供。
* 仅描述可观察行为，禁止描述实现细节。
* 类型检查以 `pyrefly` 为准，不使用 `basedpyright`。

### docs/

* 仅面向用户，描述 Usage 与 Behavior。
* 新增页面必须同步更新 `zensical.toml` 的 `nav`。
* 文档构建工具实际使用 `zensical`，配置文件是 `zensical.toml`。

## Release workflow

1. 更新 `qqmusic_api/__init__.py` 中的 `__version__` 为待发布版本。
2. 提交版本号变更：

   ```bash
   git add qqmusic_api/__init__.py
   git commit -m "🧹 chore(release): x.x.x"
   ```

3. 在**该提交上**打 tag 并推送：

   ```bash
   git tag v0.x.x
   git push origin v0.x.x
   ```

4. CI 自动执行：
   * **release.yml**：`uv build` → `uv publish`（PyPI）→ 创建 GitHub Release（git-cliff 自动生成 release body）
   * **docs.yml**（release published 后触发）：更新 `docs/release-notes.md` → 导出 `web/requirements.txt` → commit → 构建文档站 → 部署 GitHub Pages

## Agent behavior

* **核心规约**：遵循 `docs/contributing.md` 中的详细规约。**在执行任务前，必须完整阅读该指南以确保合规。**
* 仅在明确要求时，才能 `git commit` 或 `git push`。
