"""Networking module."""

from requests import Session


def get_session() -> Session:
    """Returns a custom HTTP session"""

    session = Session()
    session.headers.update({"User-Agent": "ebook-autoconverter"})
    return session
