.PHONY: .pdm ## Check if PDM is installed
.pdm:
	@pdm -V || echo 'Please install PDM: https://pdm.fming.dev/latest/#installation'

.PHONY: install ## Install dependencies and pdm run pre-commit hooks
install: .pdm
	pdm install --group :all
	pdm run pre-commit install --install-hooks

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

.PHONY: format ## Format code and check with ruff
format:
	pdm run pre-commit run ruff-format --all-files

.PHONY: lint ## Run linter checks with ruff
lint:
	pdm run pre-commit run ruff --all-files

.PHONY: typecheck ## Run type checks with mypy
typecheck:
	pdm run pre-commit run mypy --all-files

.PHONY: test ## Run tests with pytest
test: .pdm
	pdm run pytest

.PHONY: docs ## Build documentation with mkdocs
docs:
	pdm run mkdocs build --strict

.PHONY: help ## Display available Makefile targets and their descriptions
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
