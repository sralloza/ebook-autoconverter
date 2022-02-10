from functools import lru_cache

from requests import Session


@lru_cache()
def get_session():
    session = Session()
    session.headers.update({"User-Agent": "ebook-autoconverter"})
    return session
