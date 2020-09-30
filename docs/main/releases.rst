.. include:: /main/.special.rst

Release Strategy
##################################################

Micro releases: 1.0.x
    A micro release is done for any change that does not modify any existing API method.

    Any scripts that utilize this API library will work with new micro releases with no changes.

Minor releases: 1.x.0:
    A minor release is only done when an API method is removed or its signature changes.

    Any scripts that utilize this API library will work with new minor releases, although some minor changes may be required.

Major releases: x.0.0:
    A major release is only done for architectural and model changes to the API client library.

    Any scripts that utilize this API library might not work with new major releases.
