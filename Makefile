.PHONY: clean clean-test clean-pyc clean-build docs help tests uninstall_all install install_dev

tests: ## test and lint
	python3 -m pytest tests/ -v --cov=tests --cov=iss_kml -W ignore::DeprecationWarning --cov-report term-missing:skip-covered
	@echo "Linting..."
	@flake8 iss_kml/ --max-complexity=5
	@flake8 tests/ --ignore=S101,S311,F811
	@echo "\033[32mTudo certo!"
