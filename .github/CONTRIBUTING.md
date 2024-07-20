# 贡献指南

感谢您对本项目的兴趣！为了确保项目的高质量和一致性，请遵循以下指南进行贡献。

## 开发流程

1. **Fork 仓库**

   在 GitHub 上 fork 本仓库，并将 fork 后的仓库克隆到本地：

   ```sh
   git clone git@github.com:your-username/QQMusicApi.git && cd QQMusicApi
   ```

2. **配置开发环境**

   本项目 `poetry` 进行依赖管理

   ```sh
   poetry install && poetry run pre-commit install
   ```

3. **创建分支**

   从 dev 分支切换到一个新的分支再进行编码：

   ```sh
   git checkout dev && git checkout -b {分支名}
   ```

4. **开发与提交**

   开发新功能或修复 bug，并确保代码符合项目规范。完成后，提交更改：

   ```sh
   git add .
   git commit -m "描述您的更改"
   git push origin {分支名}
   ```

5. **创建 Pull Request**

   在 GitHub 上向 **`dev` 分支**发起 [Pull Request](https://github.com/luren-dc/QQMusicapi/pulls)

## pre-commit

**本项目使用 [`pre-commit`](https://github.com/pre-commit/pre-commit) 进行代码检查和格式化，确保代码的一致性和质量。**

其主要用途：
- **代码风格检查和格式化**：使用 `ruff` 工具进行代码风格检查和自动格式化。
- **类型检查**：使用 `mypy` 进行类型检查，确保代码类型安全。
- **提交信息规范**：使用 `commitizen` 确保提交信息符合规范。

## 代码规范

- 代码风格遵循 [Google Python Style](https://google.github.io/styleguide/pyguide.html)（[中文版](https://google-styleguide.readthedocs.io/zh_CN/latest/google-python-styleguide/contents.html)）
- 代码格式遵循 [PEP8](https://www.python.org/dev/peps/pep-0008/)

## 开发规范

1. 如果你增加了一个新功能，请在对应位置补充文档(docs/)
2. 请务必不要忘记注释（包括函数注释、参数类型注释、返回值注释）
3. 请保证代码可以在 `CPython3.9` 环境下运行

## 提交规范

本项目采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范

## 附录

### Git 使用参考

[Pro Git](https://progit.cn/)

### Poetry 使用参考

[Poetry](https://python-poetry.org/docs/)
