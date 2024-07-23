# 贡献指南

感谢您对本项目的兴趣！为了确保项目的高质量和一致性，请遵循以下指南进行贡献。

## 先决条件

- **Python 3.9+**
- **git**
- **virtualenv**
- **make**
- [**PDM**](https://pdm.fming.dev/latest/#installation)
- [**pre-commit**](https://pre-commit.com/)

## 开发流程

### 配置开发环境

在 GitHub 上分叉存储库并在本地克隆您的分叉。

```bash linenums="0"
git clone git@github.com:<your username>/QQMusicApi.git
cd QQMusicApi

# 安装 PDM 和 pre-commit
# https://pdm.fming.dev/latest/#installation
# https://pre-commit.com/#install
# https://pypa.github.io/pipx/
pipx install pdm
pipx install pre-commit

# 安装开发依赖
make install
```

### 切换新分支并进行更改

```bash linenums="0"
# 从 dev 分支创建并切换到新分支
git checkout -b {分支名} dev
# 开始编码
```

### 运行测试和 linting

在本地运行测试和 linting，以确保一切按预期工作。

```bash linenums="0"
# 使用 ruff 运行自动代码格式化和 linting
# https://github.com/astral-sh/ruff
make format
```

### 构建文档

如果您对文档进行了任何更改（包括对将出现在 API 文档中的函数签名、类定义或文档字符串的更改），请确保其构建成功。

```bash linenums="0"
# 构建文档
make docs
# 在 localhost:8000 上提供文档
pdm docs
```

### 创建 Pull Request

> [!WARNING]
> 请向 `dev` 分支发起 [Pull Request](https://github.com/luren-dc/QQMusicapi/pulls)

提交更改，将分支推送到 GitHub，然后创建拉取请求。

请遵循拉取请求模板并填写尽可能多的信息。链接到任何相关问题并包含您的更改的说明。

## 代码规范

- 代码风格遵循 [Google Python Style](https://google.github.io/styleguide/pyguide.html)（[中文版](https://google-styleguide.readthedocs.io/zh_CN/latest/google-python-styleguide/contents.html)）
- 代码格式遵循 [PEP8](https://www.python.org/dev/peps/pep-0008/)

## 代码注释

- 注释内容包括：模块注释、类注释、函数注释、参数类型注释、返回值注释
- 注释风格遵循 [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## 文档规范

文档使用 [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 构建

API 文档使用 [mkdocstrings](https://mkdocstrings.github.io/) 构建

- 以友好、平易近人的风格编写，易于阅读和理解，并且在保持完整的同时应尽可能简洁。
- 鼓励使用代码示例，但应保持简短。每个代码示例都应该是完整的、独立的并且可运行的。

### Markdown 拓展语法

- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/extensions)([Material for MkDocs](https://squidfunk.github.io/mkdocs-material/reference/))
- [Termynal](https://termynal.github.io/termynal.py/)
- [Markdown Exec](https://pawamoy.github.io/markdown-exec/)

## 提交规范

本项目采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范
