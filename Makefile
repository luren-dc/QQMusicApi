sources = qqmusic_api tests

.PHONY: .pdm ## Check if PDM is installed
.pdm:
	@pdm -V || echo 'Please install PDM: https://pdm.fming.dev/latest/#installation'

.PHONY: install ## Install dependencies and pre-commit hooks for development
install: .pdm
	pdm install --group :all
	pdm run pre-commit install --install-hooks

.PHONY: format ## Format code and check with ruff
format:
	pdm run ruff check $(sources)
	pdm run ruff format --check $(sources)

.PHONY: lint ## Run linter checks with ruff
lint:
	pdm run ruff check $(sources)
	pdm run ruff format --check $(sources)

.PHONY: typecheck ## Run type checks with mypy
typecheck:
	pdm run mypy --scripts-are-modules --ignore-missing-imports --check-untyped-defs $(sources)

.PHONY: test ## Run tests with pytest
test: .pdm
	pdm run pytest

.PHONY: docs ## Build documentation with mkdocs
docs:
	pdm run mkdocs build --strict

.PHONY: clean ## Remove build artifacts and cache files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf docs/_build
	rm -rf dist
	rm -rf .mypy_cache
	rm -rf .cache

.PHONY: help ## Display this message
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
