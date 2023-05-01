#!/usr/bin/env python
"""CLI for Cloudflare utilities."""

if __name__ == "__main__":  # pragma: no cover
    import sys
    import pathlib

    THIS_PATH = pathlib.Path(__file__).parent.absolute()

    sys.path.insert(0, str(THIS_PATH))

    from cf_token import cli

    cli.get_token_cli()
