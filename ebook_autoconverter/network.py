from functools import lru_cache

from requests import Session


@lru_cache()
def get_session():
    return Session()
