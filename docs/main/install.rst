.. include:: /main/.special.rst

.. _installation:

Installation
#########################

Install Python
============================================================

Download and install a :ref:`supported version<supported_versions>` of `python`_ for your platform.

If installing on Windows, make sure you check the option to add Python to the PATH.
This will ensure that not only the `python` and `pip` binaries are on the path,
but that the `axonshell` CLI script that comes with this package will be available on
the PATH after you install it.

Install the package using `pip`_
============================================================

axonius-api-client is listed on `pypi`_, so you can do pip install from any
platform that has python installed.

.. code-block:: console

  $ pip install axonius_api_client

Offline installs using `pip`_
============================================================

If you need to install axonius-api-client to a system that doesn't have
access to the internet, there are a few hoops to jump through.

.. note::
    You will need to install the exact same version of `python`_ on both systems.

    If the destination system is linux, the source system should be the exact same linux
    distribution, version, and build.

.. note::
    On Windows, each system should have should the
    `PATH variable updated`_ to include the Python directories:

    * ``C:\Program Files\Python38``
    * ``C:\Program Files\Python38\Scripts``

On the source system that does have internet access, use the following command to download
all of the requirements as wheel packages:

.. code-block:: console

   $ pip download -d d:\axonshell_pkg axonius-api-client --only-binary

Copy the contents of d:\axonshell_pkg to the destination server, and then on the
destination server run:

.. code-block:: console

   $ pip install --no-index --find-links d:\axonshell_pkg --target d:\axonshell axonius-api-client

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
.. _PATH variable updated: https://projects.raspberrypi.org/en/projects/using-pip-on-windows/5
