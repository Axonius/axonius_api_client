.. include:: /root/.special.rst
Releases
##################################################

Strategy
==================================================

Micro releases: 1.0.x
    A micro release is done for any change that does not modify any existing API method.

Minor releases: 1.x.0:
    A minor release is only done when an API method is removed or its signature changes.

Major releases: x.0.0:
    A major release is only done for architectural and model changes to the API client library. Any scripts that utilize this API library will probably not work in between major releases.

Todo
==================================================

2.0.0
--------------------------------------------------
* :green:`docs`: Add shell examples.
* :green:`docs`: Add API examples.

2.1.0
--------------------------------------------------
* :blue:`api`: api.Enforcements flush out.
* :blue:`rest_api`: Flush out enforcement routes in REST API server.

Changelog
==================================================

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
