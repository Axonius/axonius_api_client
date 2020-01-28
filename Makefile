PACKAGE := axonius_api_client
VERSION := $(shell grep "^__version__" $(PACKAGE)/version.py | cut -d\" -f2)
PYVER := $(cat .python_version)

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

pipenv_clean:
	pipenv --rm || true

pyenv_init:
	pyenv install $(PYVER) -s || true
	pyenv local $(PYVER) || true

lint:
	pipenv run isort -rc -y $(PACKAGE) setup.py axonshell*.py
	pipenv run pipenv run black -l 89 $(PACKAGE) setup.py axonshell*.py
	pipenv run pydocstyle --match='(?!test_).*\.py' $(PACKAGE) setup.py axonshell*.py
	pipenv run flake8 --max-line-length 89 $(PACKAGE) setup.py axonshell*.py
	pipenv run bandit --skip B101 -r $(PACKAGE)

test:
	pipenv run pytest -ra --verbose --cov-config=.coveragerc --cov-report xml --cov-report=html:cov_html --cov=$(PACKAGE) --showlocals  --exitfirst $(PACKAGE)/tests

test_dev:
	pipenv run pytest -vv --showlocals --exitfirst --last-failed $(PACKAGE)/tests

test_cov_open:
	open cov_html/index.html

test_clean:
	rm -rf .egg .eggs junit-report.xml cov_html .tox .pytest_cache .coverage coverage.xml

docs:
	(cd docs && pipenv run make html SPHINXOPTS="-Wna" && cd ..)

docs_dev:
	(cd docs && pipenv run make html SPHINXOPTS="-na" && cd ..)

docs_apigen:
	pip install sphinx -t /tmp/sphinx-latest --quiet --upgrade
	rm -rf docs/main/api
	PYTHONPATH=/tmp/sphinx-latest /tmp/sphinx-latest/bin/sphinx-apidoc -e -P -M -f -T -t docs/_templates -o docs/main/api $(PACKAGE) $(PACKAGE)/tests $(PACKAGE)/cli

docs_open:
	open docs/_build/html/index.html

docs_coverage:
	(cd docs && pipenv run make coverage && cd ..)
	cat docs/_build/coverage/python.txt

docs_linkcheck:
	(cd docs && pipenv run make linkcheck && cd ..)
	cat docs/_build/linkcheck/output.txt

docs_clean:
	rm -rf docs/_build

docs_dumprefs:
	pipenv run python -m sphinx.ext.intersphinx docs/_build/html/objects.inv

git_check:
	@git diff-index --quiet HEAD && echo "*** REPO IS CLEAN" || (echo "!!! REPO IS DIRTY"; false)
	@git tag | grep "$(VERSION)" && echo "*** FOUND TAG: $(VERSION)" || (echo "!!! NO TAG FOUND: $(VERSION)"; false)

git_tag:
	@git tag "$(VERSION)"
	@git push --tags
	@echo "*** ADDED TAG: $(VERSION)"

pkg_publish:
	# FUTURE: add check that only master branch can publish / git tag
	$(MAKE) pkg_build
	$(MAKE) git_check
	pipenv run twine upload dist/*

pkg_build:
	$(MAKE) pkg_clean

	@echo "*** Building Source and Wheel (universal) distribution"
	pipenv run python setup.py sdist bdist_wheel --universal

	@echo "*** Checking package with twine"
	pipenv run twine check dist/*

pkg_install:
	$(MAKE) pkg_build
	pip install dist/*.whl --upgrade

pkg_clean:
	rm -rf build dist *.egg-info

files_clean:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name ".DS_Store" | xargs rm -f
	find . -type f -name "*.pyc" | xargs rm -f

clean:
	$(MAKE) files_clean
	$(MAKE) pkg_clean
	$(MAKE) test_clean
	$(MAKE) docs_clean
	$(MAKE) pipenv_clean

# FUTURE: add cov_publish
