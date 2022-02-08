PACKAGE := axonius_api_client
VERSION := $(shell python get_version.py)
PYVER   := $(shell cat .python-version)

.PHONY: build docs

help:
	@cat Makefile.help

init:
	echo ">>>>>>>> INITIALIZING FOR VERSION: $(VERSION) PYTHON $(PYVER)"
	$(MAKE) pip_install_tools
	$(MAKE) clean
	$(MAKE) pipenv_init
	$(MAKE) pipenv_install_lint
	$(MAKE) pipenv_install_dev
	$(MAKE) pipenv_install_docs
	$(MAKE) pipenv_install_build

init_ver:
	echo ">>>>>>>> INITIALIZING FOR VERSION: $(VERSION) PYTHON $(PYVER)"
	$(MAKE) pip_install_tools
	$(MAKE) clean
	$(MAKE) pipenv_init_ver
	$(MAKE) pipenv_install_lint
	$(MAKE) pipenv_install_dev
	$(MAKE) pipenv_install_docs
	$(MAKE) pipenv_install_build

pip_install_tools:
	pip install \
		--quiet \
		--upgrade \
		--requirement requirements-pkg.txt

pipenv_install_dev:
	pipenv run pip install \
		--quiet \
		--upgrade \
		--requirement requirements-dev.txt

pip_install_lint:
	pip install \
		--quiet \
		--upgrade \
		--requirement requirements-lint.txt

pipenv_install_lint:
	pipenv run pip install \
		--quiet \
		--upgrade \
		--requirement requirements-lint.txt

pipenv_install_build:
	pipenv run pip install \
		--quiet \
		--upgrade \
		--requirement requirements-build.txt

pipenv_install_docs:
	pipenv run pip install \
		--quiet \
		--upgrade \
		--requirement docs/requirements.txt

pipenv_init:
	pipenv install \
		--dev \
		--skip-lock

pipenv_init_ver:
	pipenv install \
		--dev \
		--skip-lock \
		--python $(PYVER)

pipenv_clean:
	pipenv --rm || true

lint:
	pipenv run isort \
		$(PACKAGE) setup.py shell.py
	pipenv run black \
		-l 100 \
		$(PACKAGE) setup.py shell.py
	pipenv run flake8 \
		--max-line-length 100 \
		--exclude $(PACKAGE)/tests \
		--exclude $(PACKAGE)/examples \
		$(PACKAGE) setup.py shell.py
	# XXX DISABLED FOR NOW
	# 	pipenv run pydocstyle \
	# 		--match-dir='(?!tests).*'\
	# 		--match-dir='(?!examples).*' \
	# 		$(PACKAGE) setup.py shell.py
	# 	pipenv run bandit \
	# 		-x $(PACKAGE)/examples,$(PACKAGE)/tests \
	# 		--skip B101,B107 \
	# 		-r \
	# 		$(PACKAGE)

cov_open:
	open artifacts/cov_html/index.html

clean_tests:
	rm -rf .egg .eggs .tox .pytest_cache artifacts/

docs:
	(cd docs && pipenv run make html SPHINXOPTS="-Wna" && cd ..)

docs_dev:
	(cd docs && pipenv run make html SPHINXOPTS="-na" && cd ..)

docs_apigen:
	pip install sphinx -t /tmp/sphinx-latest --quiet --upgrade
	rm -rf /tmp/api
	PYTHONPATH=/tmp/sphinx-latest /tmp/sphinx-latest/bin/sphinx-apidoc \
		-e -P -M -f -T -t docs/_templates \
		-o /tmp/api $(PACKAGE) $(PACKAGE)/tests $(PACKAGE)/cli

docs_open:
	open docs/_build/html/index.html

docs_coverage:
	(cd docs && pipenv run make coverage && cd ..)
	cat docs/_build/coverage/python.txt

docs_linkcheck:
	(cd docs && pipenv run make linkcheck && cd ..)
	cat docs/_build/linkcheck/output.txt

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
	pipenv run twine upload artifacts/dist/*

pkg_build:
	$(MAKE) clean_pkg

	@echo "*** Building Source and Wheel (universal) distribution"
	pipenv run python setup.py sdist bdist_wheel --universal --dist-dir artifacts/dist

	@echo "*** Checking package with twine"
	pipenv run twine check artifacts/dist/*

pkg_install:
	$(MAKE) pkg_build
	pip install artifacts/dist/*.whl --upgrade

clean_docs:
	rm -rf docs/_build

clean_pkg:
	rm -rf dist build artifacts/dist axonius_api_client.egg-info

clean_files:
	find . -type d -name "__pycache__" | xargs rm -rf
	find . -type f -name ".DS_Store" | xargs rm -f
	find . -type f -name "*.pyc" | xargs rm -f
	rm -f axonius_api_client.log*

clean:
	$(MAKE) clean_files
	$(MAKE) clean_pkg
	$(MAKE) clean_tests
	$(MAKE) clean_docs
	$(MAKE) pipenv_clean
