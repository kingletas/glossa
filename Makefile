.DEFAULT_GOAL := help

.PHONY: help
help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

.PHONY: check
check: ## Everything a commit has to pass: ruff and the tests
	@uv run ruff check .
	@uv run pytest -q

.PHONY: test
test: ## Run the test suite only
	@uv run pytest -q
