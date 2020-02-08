.. include:: /main/.special.rst

Contribution
###################################################

We welcome all contributions to `axonius-api-client`.

Support
===================================================

For any support requests, bug reports, or feature requests you can:

* Open an issue in the `issue tracker`_
* Send an email apiclient@axonius.com

Reporting Issues
===================================================

When reporting issues, please include information for:

- Python distribution and version
- Operating System platform and version
- `axonius-api-client` version
- Full tracebacks of any exceptions

Submitting Patches
===================================================

All patches should be submitted as pull requests on the `GitHub project`_.

- Clearly explain what you're trying to accomplish.

- Include tests for any changes.

- Ensure the full :ref:`testing-suite` runs without any errors before submitting
  a pull request.

- Ensure the test coverage reports 100% before submitting a pull request.

- Follow :pep:`8`.

- Use `isort`_ and `black`_ to format your code and `flake8`_, `pydocstyle`_,
  and `bandit`_ to lint your code:

.. code-block:: shell

   $ isort -rc -y axonius_api_client setup.py axonshell*.py
   $ black axonius_api_client setup.py axonshell*.py
   $ pydocstyle axonius_api_client setup.py axonshell*.py
   $ flake8 --max-line-length 89 axonius_api_client setup.py axonshell*.py
   $ bandit --skip B101 -r axonius_api_client

.. _testing-suite:

Testing Suite
===================================================

`axonius-api-client` uses `pytest`_ as it's test suite.

To run the tests, create a .env file with the connection information:

.. code-block:: shell

   $ echo 'AX_URL=x' >> .env
   $ echo 'AX_KEY=x' >> .env
   $ echo 'AX_SECRET=x' >> .env

You can also supply the connection information as arguments to pytest ala:

.. code-block:: shell

   $ pytest --ax-url=x --ax-key=x --ax-secret=x ...

Then run the full test suite and generate test coverage in html format
to `cov_html/index.html`:

.. code-block:: shell

   $ pytest \
     -ra \
     --verbose \
     --cov-config=.coveragerc \
     --cov-report=html:cov_html \
     --cov=axonius_api_client \
     --showlocals  \
     --exitfirst \
     axonius_api_client/tests

Supported Python versions
----------------------------------------------------------

* Latest versions of 3.7 and 3.8
* Windows, macOS, Linux

Tested Python versions
----------------------------------------------------------

* 3.8.1 on macOS 10.15.3 (Catalina)
* 3.8.1 on Windows 10
* 3.8.1 on Ubuntu Linux 18.04

.. note::

   Python 2.7 reached its end-of-life on 01/01/2020, and therefore is no longer supported.

.. _issue tracker: https://github.com/Axonius/axonius_api_client/issues
.. _GitHub project: https://github.com/Axonius/axonius_api_client
.. _black: https://github.com/psf/black
.. _flake8: https://gitlab.com/pycqa/flake8
.. _pytest: https://docs.pytest.org/en/latest/
.. _isort: https://github.com/timothycrosley/isort
.. _pydocstyle: https://github.com/PyCQA/pydocstyle/
.. _bandit: https://github.com/PyCQA/bandit
