"""安装开发环境"""

import os

# 安装依赖
os.system("pdm install --group :all")
# 安装 git hooks
os.system("pre-commit install --install-hooks")
