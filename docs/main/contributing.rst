.. include:: /main/.special.rst

Contribution
###################################################

We welcome all contributions to `axonius-api-client`.

Support
===================================================

For any support requests, bug reports, or feature requests you can:

* Open an issue in the `issue tracker`_
* Send an email support@axonius.com

Reporting Issues
===================================================

When reporting issues, please include information for:

- Output of ``axonshell tools sysinfo``
- Tracebacks of any exceptions
- Log file

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

  $ isort \
    axonius_api_client setup.py shell.py
  $ black \
    -l 100 \
    axonius_api_client setup.py shell.py
  $ pydocstyle \
    --match-dir='(?!tests).*'\
    --match-dir='(?!examples).*' \
    axonius_api_client setup.py shell.py
  $ flake8 \
    --max-line-length 100 \
    axonius_api_client setup.py shell.py
  $ bandit \
    -x axonius_api_client/examples,axonius_api_client/tests \
    --skip B101 \
    -r \
    axonius_api_client

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

.. _supported_versions:

Supported Python versions
----------------------------------------------------------

* Latest versions of 3.7 and 3.8
* Microsoft Windows, macOS, Linux

.. note::

   Python 2.7 reached its end-of-life on 01/01/2020, and
   therefore is no longer supported as of API client v2.2.0.

Tested Python versions
----------------------------------------------------------

* macOS 10.15.3 (Catalina)

  * Python 3.7.6 64 bit: 02/08/2020
  * Python 3.8.1 64 bit : 02/08/2020

* Ubuntu Linux 18.04.03 LTS 64 bit

  * Python 3.7.6 64 bit: 02/08/2020
  * Python 3.8.1 64 bit: 02/08/2020

* Microsoft Windows 10 Pro x64 (Version 1909, Build 18363.592)

  * Python 3.8.1 64 bit: 02/08/2020

* Microsoft Windows Server 2012 R2 x64 (Version 6.3, Build 9600)

  * Python 3.8.1 64 bit: 02/08/2020

* Microsoft Windows Server 2019 x64 (Version 1809, Build 17763.1012)

  * Python 3.8.1 64 bit: 02/08/2020

.. _issue tracker: https://github.com/Axonius/axonius_api_client/issues
.. _GitHub project: https://github.com/Axonius/axonius_api_client
.. _black: https://github.com/psf/black
.. _flake8: https://gitlab.com/pycqa/flake8
.. _pytest: https://docs.pytest.org/en/latest/
.. _isort: https://github.com/timothycrosley/isort
.. _pydocstyle: https://github.com/PyCQA/pydocstyle/
.. _bandit: https://github.com/PyCQA/bandit

Release Strategy
===================================================

Micro releases: 1.0.x
    A micro release is done for any change that does not modify any existing API method.

    Any scripts that utilize this API library will work with new micro releases with no changes.

Minor releases: 1.x.0:
    A minor release is only done when an API method is removed or its signature changes.

    Any scripts that utilize this API library will work with new minor releases, although some minor changes may be required.

Major releases: x.0.0:
    A major release is only done for architectural and model changes to the API client library.

    Any scripts that utilize this API library might not work with new major releases.
