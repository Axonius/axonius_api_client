PACKAGE := "axonius_api_client"
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\' -f2)

.PHONY: build
init:
	$(MAKE) pkg_tools
	$(MAKE) pipenv_clean
	$(MAKE) pipenv_init

pkg_tools:
	pip install --quiet --upgrade pip disttools pipenv

pipenv_clean:
	pipenv --rm || true

pipenv_init:
	pipenv install --dev --skip-lock

lint:
	pipenv run pip install --quiet --upgrade --requirement requirements-dev.txt
	pipenv run black --line-length=120 -S .
	pipenv run pylint --rcfile=".pylintrc" $(PACKAGE)
	pipenv run pylint --rcfile=".pylintrc" setup.py

build:
	$(MAKE) clean_dist

	pipenv run pip install --quiet --upgrade --requirement requirements-build.txt

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
