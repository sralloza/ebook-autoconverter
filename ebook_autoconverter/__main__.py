"""Module to make package executable."""

from time import time

from .core import update_books

if __name__ == "__main__":
    t0 = time()
    update_books()
    t1 = time()
    print(f"Job done in {t1-t0:.2f} seconds")
