.PHONY: install test check docs-check docs-build run-all quick help

help:
	@echo "ChaosRL: Autonomous RL Chaos Engineering"
	@echo "make install     Install package in editable mode"
	@echo "make test        Run unit tests"
	@echo "make check       Run stage exit criteria check"
	@echo "make docs-check  Verify documentation integrity"
	@echo "make docs-build  Build documentation from facts registry"
	@echo "make run-all     Run end-to-end execution"
	@echo "make quick       Run quick smoke test across all stages"

install:
	pip install -e .

test:
	pytest tests/ -v

check:
	python -m chaosrl check --all

docs-check:
	python -m chaosrl docs-check --all

docs-build:
	python -m chaosrl docs-build

run-all:
	python -m chaosrl run-all

quick:
	python -m chaosrl quick

