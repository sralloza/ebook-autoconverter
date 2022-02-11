import os
import sys

EXEC = "/usr/bin/ebook-convert"
try:
    URL = os.environ["CALIBRE_WEB_URL"]
    USERNAME = os.environ["CALIBRE_WEB_USERNAME"]
    PASSWORD = os.environ["CALIBRE_WEB_PASSWORD"]
except KeyError as exc:
    print(f"Must set environment variable {exc}")
    sys.exit(1)

FORCE_CONVERSION = os.getenv("FORCE_CONVERSION", "").lower() == "true"
DISABLE_LOGIN_TOKEN = os.getenv("DISABLE_LOGIN_TOKEN", "").lower() == "true"
