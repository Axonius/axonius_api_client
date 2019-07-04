PACKAGE := "axonius_api_client"
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\' -f2)

.PHONY: build
init:
	$(MAKE) pip_install_tools
	$(MAKE) clean
	$(MAKE) pyenv_init
	$(MAKE) pipenv_init

pip_install_tools:
	pip install --quiet --upgrade --requirement requirements-pkg.txt

pipenv_install_dev:
	pipenv run pip install --quiet --upgrade --requirement requirements-dev.txt

pipenv_install_lint:
	pipenv run pip install --quiet --upgrade --requirement requirements-lint.txt

pipenv_install_build:
	pipenv run pip install --quiet --upgrade --requirement requirements-build.txt

pipenv_clean:
	pipenv --rm || true

pipenv_init:
	pipenv install --dev --skip-lock

pyenv_init:
	pyenv install 3.7.3 -s
	pyenv install 3.6.8 -s
	pyenv install 2.7.16 -s
	pyenv local 3.7.3 3.6.8 2.7.16

lint:
	$(MAKE) pipenv_install_lint
	pipenv run which black && black $(PACKAGE) setup.py
	pipenv run flake8 --max-line-length 89 $(PACKAGE) setup.py
	pipenv run bandit -r . --skip B101 -x playground.py,setup.py

test_debug:
	$(MAKE) pipenv_install_dev
	pipenv run pytest --capture=no --showlocals --log-cli-level=DEBUG --verbose --exitfirst $(PACKAGE)/tests

test:
	$(MAKE) pipenv_install_dev
	pipenv run pytest --junitxml=junit-report.xml --cov-config=.coveragerc --cov-report=term --cov-report xml --cov-report=html:cov_html --cov=$(PACKAGE) --showlocals --log-cli-level=INFO --verbose --exitfirst $(PACKAGE)/tests

build:
	$(MAKE) clean_dist
	$(MAKE) pipenv_install_build

	@echo "*** Building Source and Wheel (universal) distribution"
	pipenv run python setup.py sdist bdist_wheel --universal

	@echo "*** Checking package with twine"
	pipenv run twine check dist/*

clean_files:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name ".DS_Store" | xargs rm -f
	find . -type f -name "*.pyc" | xargs rm -f

clean_dist:
	rm -rf build dist *.egg-info

clean_test:
	rm -rf .egg .eggs junit-report.xml cov_html .tox .pytest_cache .coverage

clean:
	$(MAKE) clean_dist
	$(MAKE) clean_files
	$(MAKE) clean_test
	$(MAKE) pipenv_clean

git_check:
	@git diff-index --quiet HEAD && echo "*** REPO IS CLEAN" || (echo "!!! REPO IS DIRTY"; false)
	@git tag | grep "$(VERSION)" && echo "*** FOUND TAG: $(VERSION)" || (echo "!!! NO TAG FOUND: $(VERSION)"; false)

git_tag:
	@git tag "$(VERSION)"
	@git push --tags
	@echo "*** ADDED TAG: $(VERSION)"

publish:
	$(MAKE) lint
	$(MAKE) build
	$(MAKE) git_check
	pipenv run twine upload dist/*
