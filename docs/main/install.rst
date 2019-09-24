.. include:: /main/.special.rst

.. _installation:

Installation
#########################

Install Python
============================================================

Download and install the latest 3.7 version of `python`_ for your platform.

If installing on Windows, make sure you check the option to add Python to the PATH.
This will ensure that not only the `python` and `pip` binaries are on the path,
but that the `axonshell` CLI script that comes with this package will be available on
the PATH after you install it.

.. note::

   While 2.7 is supported, using it is not recommended due to the `pending EOL on January 1st 2020 <pyeol>`_.

Install the package using `pip`_
============================================================

axonius-api-client is listed on `pypi`_, so you can do pip install from any
platform that has python installed.

.. code-block:: console

  $ pip install axonius_api_client

Install the package Using `pipenv`_
============================================================

pipenv makes it easy to create virtual environments for python projects.

.. code-block:: console

  $ pipenv install axonius_api_client

Download the entire repository using `git`_
============================================================

This is really only for those who wish to contribute to this project, although
you can install the package after cloning the repository using ``python setup.py install``.

.. code-block:: console

  $ git clone git://github.com/Axonius/axonius_api_client.git

Browse the repository on `GitHub`_
============================================================

The master branch will always be the most recent stable version.

.. _git: https://git-scm.com/
.. _pipenv: https://pipenv.readthedocs.io/en/latest/
.. _pip: https://pypi.org/project/pip/
.. _GitHub: https://github.com/Axonius/axonius_api_client
.. _pypi: https://pypi.org/project/axonius-api-client/
.. _python: https://www.python.org/downloads/
.. _pyeol: https://python3statement.org
