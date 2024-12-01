"""安装开发环境"""

import os

# 安装依赖
os.system("uv sync --all-groups")
# 安装 git hooks
os.system("pre-commit install --install-hooks")
