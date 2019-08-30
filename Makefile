PACKAGE := axonius_api_client
VERSION := $(shell grep __version__ $(PACKAGE)/version.py | cut -d\" -f2)

.PHONY: build docs

help:
	@cat Makefile.help

init:
	$(MAKE) pip_install_tools
	$(MAKE) clean
	$(MAKE) pyenv_init
	$(MAKE) pipenv_init
	$(MAKE) pipenv_install_lint
	$(MAKE) pipenv_install_dev
	$(MAKE) pipenv_install_docs
	$(MAKE) pipenv_install_build

pip_install_tools:
	pip install --quiet --upgrade --requirement requirements-pkg.txt

pipenv_install_dev:
	pipenv run pip install --quiet --upgrade --requirement requirements-dev.txt

pipenv_install_lint:
	pipenv run pip install --quiet --upgrade --requirement requirements-lint.txt

pipenv_install_build:
	pipenv run pip install --quiet --upgrade --requirement requirements-build.txt

pipenv_install_docs:
	pipenv run pip install --quiet --upgrade --requirement docs/requirements.txt

pipenv_init:
	pipenv install --dev --skip-lock

pyenv_init:
	pyenv install 3.7.4 -s || true
	pyenv local 3.7.4 || true

lint:
	pipenv run isort -rc -y $(PACKAGE) setup.py axonshell*.py
	pipenv run which black && black $(PACKAGE) setup.py axonshell*.py
	pipenv run pydocstyle $(PACKAGE) setup.py axonshell*.py
	pipenv run flake8 --max-line-length 89 $(PACKAGE) setup.py axonshell*.py
	pipenv run bandit --skip B101 -r $(PACKAGE)

test:
	# --cov-report=term --log-cli-level=INFO --verbose -rA
	pipenv run pytest --junitxml=junit-report.xml --cov-config=.coveragerc --cov-report xml --cov-report=html:cov_html --cov=$(PACKAGE) --showlocals  --exitfirst $(PACKAGE)/tests

test_debug:
# 	pipenv run pytest -rA --capture=no --showlocals --log-cli-level=DEBUG --verbose --exitfirst $(PACKAGE)/tests
	pipenv run pytest --showlocals --exitfirst $(PACKAGE)/tests

cov_open:
	open cov_html/index.html

docs:
	(cd docs && pipenv run make html SPHINXOPTS="-Wna" && cd ..)

docs_open:
	open docs/_build/html/index.html

docs_coverage:
	(cd docs && pipenv run make coverage && cd ..)
	cat docs/_build/coverage/python.txt

docs_linkcheck:
	(cd docs && pipenv run make linkcheck && cd ..)
	cat docs/_build/linkcheck/output.txt

git_check:
	@git diff-index --quiet HEAD && echo "*** REPO IS CLEAN" || (echo "!!! REPO IS DIRTY"; false)
	@git tag | grep "$(VERSION)" && echo "*** FOUND TAG: $(VERSION)" || (echo "!!! NO TAG FOUND: $(VERSION)"; false)

git_tag:
	@git tag "$(VERSION)"
	@git push --tags
	@echo "*** ADDED TAG: $(VERSION)"

pkg_publish:
	# FUTURE: add check that only master branch can publish / git tag
	# FUTURE: add cov_publish
	$(MAKE) lint
	$(MAKE) pkg_build
	$(MAKE) git_check
	pipenv run twine upload dist/*

pkg_build:
	$(MAKE) clean_build

	@echo "*** Building Source and Wheel (universal) distribution"
	pipenv run python setup.py sdist bdist_wheel --universal

	@echo "*** Checking package with twine"
	pipenv run twine check dist/*

clean_build:
	rm -rf build dist *.egg-info

clean_files:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name ".DS_Store" | xargs rm -f
	find . -type f -name "*.pyc" | xargs rm -f

clean_tests:
	rm -rf .egg .eggs junit-report.xml cov_html .tox .pytest_cache .coverage

clean_docs:
	rm -rf docs/_build

clean_pipenv:
	pipenv --rm || true

clean:
	$(MAKE) clean_files
	$(MAKE) clean_build
	$(MAKE) clean_tests
	$(MAKE) clean_docs
	$(MAKE) clean_pipenv
