PYTHON_VERSION ?= 3.10
PYTHON ?= python$(PYTHON_VERSION)
PIP ?= $(PYTHON) -m pip
PIPENV ?= $(PYTHON) -m pipenv
PIPENV_PYTHON = $(PIPENV) run python
PIPENV_PIP = $(PIPENV_PYTHON) -m pip
PWD = $(shell pwd)


PHONY: pipenv
pipenv:
	$(PIP) install pip==23.3.2
	$(PIP) install pipenv==2023.11.17

.PHONY: setup
setup: pipenv
	$(PIPENV) install --verbose --python $(PYTHON_VERSION)

.PHONY: setup-dev
setup-dev: pipenv
	$(PIPENV) install --verbose --dev --python $(PYTHON_VERSION)
	-$(PIPENV) run mypy --install-types --non-interactive

.PHONY: export-requirements
export-requirements: pipenv
	$(PIPENV) run pip freeze > requirements.txt

clean-env:
	$(PIPENV) --rm

reports:
	mkdir -p reports

.PHONY: style
style: reports pipenv
	@echo -n > reports/flake8_errors.log
	@echo -n > reports/mypy_errors.log
	@echo -n > reports/mypy.log
	@echo

	-$(PIPENV) run flake8 | tee -a reports/flake8_errors.log
	@if [ -s reports/flake8_errors.log ]; then exit 1; fi

	-$(PIPENV) run mypy . --check-untyped-defs | tee -a reports/mypy.log
	@if ! grep -Eq "Success: no issues found in [0-9]+ source files" reports/mypy.log ; then exit 1; fi

.PHONY: format
format: pipenv
	$(PIPENV) run isort .
	$(PIPENV) run black .

.PHONY: isort
isort: pipenv
	$(PIPENV) run isort .

.PHONY: black
black: pipenv
	$(PIPENV) run black .

.PHONY: test
test: reports
	@bash -c 'set -o pipefail; export PYTHONPATH=$(PWD); \
	$(PIPENV) run pytest -v --junitxml=reports/junit.xml \
	--html=./reports/pytest.html \
	--cov=llm-docstring-generator \
	--cov-report term \
	--cov-report html:./reports/coverage.html \
    -o log_cli=true -o log_level=INFO -o log_file=reports/tests.log \
    tests/* 2>&1 | tee reports/tests.log'

.PHONY: shell
shell:
	$(PIPENV) shell


# create package
.PHONY: package
package: setup-dev
	$(PIPENV) run python setup.py sdist bdist_wheel
