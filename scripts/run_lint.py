"""代码检查脚本"""

import os

path = os.path.dirname(os.path.abspath(__file__))

sources = ["qqmusic_api", "tests", "examples"]

os.system(f"pdm run ruff format --check {' '.join(sources)}")
os.system(f"pdm run mypy --scripts-are-modules --ignore-missing-imports --check-untyped-defs {' '.join(sources) }")
