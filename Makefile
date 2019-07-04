PACKAGE := "axonius_api_client"
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\' -f2)

.PHONY: build
init:
	$(MAKE) pkg_tools
	$(MAKE) pipenv_clean
	$(MAKE) pipenv_init

pkg_tools:
	pip install --quiet --upgrade --requirement requirements-pkg.txt

pkg_dev:
	pip install --quiet --upgrade --requirement requirements-dev.txt

pkg_lint:
	pip install --quiet --upgrade --requirement requirements-lint.txt

pkg_build:
	pip install --quiet --upgrade --requirement requirements-build.txt

pipenv_clean:
	pipenv --rm || true

pipenv_init:
	pipenv install --dev --skip-lock

lint:
	$(MAKE) pkg_lint
	pipenv run which black && black $(PACKAGE) setup.py
	pipenv run flake8 --max-line-length 89 $(PACKAGE) setup.py
	pipenv run bandit -r . --skip B101 -x playground.py,setup.py

test:
	$(MAKE) pkg_dev
	pipenv run pytest --capture=no --showlocals --log-cli-level=DEBUG --verbose --exitfirst $(PACKAGE)/tests

test_coverage:
	$(MAKE) pkg_dev
	pipenv run pytest --junitxml=junit-report.xml --cov-config=.coveragerc --cov-report=term --cov-report xml --cov-report=html:cov_html --cov=$(PACKAGE) --capture=no --showlocals --log-cli-level=DEBUG --verbose --exitfirst $(PACKAGE)/tests

build:
	$(MAKE) clean_dist
	$(MAKE) pkg_build

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
