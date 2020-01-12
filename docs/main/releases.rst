.. include:: /main/.special.rst

Releases
##################################################

Strategy
==================================================

Micro releases: 1.0.x
    A micro release is done for any change that does not modify any existing API method.

    Any scripts that utilize this API library will work with new micro releases with no changes.

Minor releases: 1.x.0:
    A minor release is only done when an API method is removed or its signature changes.

    Any scripts that utilize this API library will work with new minor releases, although some minor changes may be required.

Major releases: x.0.0:
    A major release is only done for architectural and model changes to the API client library.

    Any scripts that utilize this API library might not work with new major releases.

Changelog
==================================================

`2.1.4`_ (2020-01-12)
--------------------------------------------------
* :red:`bugfix`: Fixed a minor issue with text string 'False' not being recognized as an alternative for boolean False.
* :red:`bugfix`: Fixed a minor issue with selecting an adapter connection by ID.
* :blue:`enhancement`: You can now specify fields to fetch in addition to the fields defined in a saved-query. References:
  * :ref:`fr_214_5`
* :blue:`enhancement`: You can now specify fields using regular expressions whereever fields can be specified. References:
  * :ref:`fr_214_3`
  * :ref:`fr_214_4`
* :blue:`enhancement`: You can use show-config when adding new connections to see the configuration without being prompted. References:
  * :ref:`fr_214_1`
  * :ref:`fr_214_2`

`2.0.0`_ (2019-09-16)
--------------------------------------------------
* :blue:`major release`: major refactor
* incompatible with 1.0 API calls.
* Added a command line interface :axon:`axonshell`.
* Adapters and adapter connections now have user-friendly methods.

`1.0.0`_ (2019-07-05)
--------------------------------------------------
* :blue:`major release`: initial release

.. _1.0.0: https://github.com/Axonius/axonius_api_client/releases/tag/1.0.0
.. _2.0.0: https://github.com/Axonius/axonius_api_client/releases/tag/2.0.0
.. _2.1.4: https://github.com/Axonius/axonius_api_client/releases/tag/2.1.4
