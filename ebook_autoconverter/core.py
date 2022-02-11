from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from requests import Response

from .calibre import convert_ebook
from .config import FORCE_CONVERSION, PASSWORD, URL, USERNAME
from .network import get_session


def login():
    session = get_session()
    res = session.get(URL + "/login")
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    token_container = soup.find("input", {"name": "csrf_token"})

    if token_container is None:
        raise ValueError(f"Can't find token (res={res}, url={res.url})")

    token = token_container["value"]

    data = {
        "next": "/",
        "csrf_token": token,
        "username": USERNAME,
        "password": PASSWORD,
        "submit": "",
    }
    res = session.post(URL + "/login", data=data)
    res.raise_for_status()


def get_books():
    session = get_session()
    res = session.get(URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    pags = soup.find("div", {"class": "pagination"})
    if pags is None:
        ids = find_books(res)
        ids.sort()
        print(f"Found {len(ids)} books (no pages): {ids}")
        return ids

    pages = set()
    for link in pags.find_all("a"):
        pages.add(link["href"])

    if len(pages) > 1:
        ids = []
        for link in pages:
            res_extra = session.get(URL + link)
            res_extra.raise_for_status()
            ids += find_books(res_extra)
    else:
        ids = find_books(res)

    ids.sort()
    print(f"Found {len(ids)} books ({len(pages)} pages): {ids}")
    return ids


def find_books(res: Response) -> List[int]:
    soup = BeautifulSoup(res.text, "html.parser")
    covers = soup.find_all("div", {"class": "meta"})
    links = []
    for cover in covers:
        links.append(cover.a["href"])

    ids = [int(x.split("/")[-1]) for x in links]
    return ids


def process_book(book_id: int, force: bool = False):
    if force:
        print(f"Force fixing book {book_id}")
        return convert_and_upload_book(book_id)

    session = get_session()
    res = session.head(URL + f"/download/{book_id}/azw3/x")
    if res.status_code == 404:
        print(f"Fixing book {book_id}")
        return convert_and_upload_book(book_id)

    print(f"Book {book_id} is OK")


def convert_and_upload_book(book_id: int):
    session = get_session()
    ebook_path = Path("tmp.epub")
    res1 = session.get(URL + f"/download/{book_id}/epub/x")
    res1.raise_for_status()
    ebook_path.write_bytes(res1.content)
    try:
        azw3_path = convert_ebook("tmp.epub")
    except:
        ebook_path.unlink()
        raise

    res2 = session.get(URL + f"/admin/book/{book_id}")
    res2.raise_for_status()
    soup = BeautifulSoup(res2.text, "html.parser")
    token_container = soup.find("input", {"name": "csrf_token"})

    if token_container is None:
        raise ValueError(f"Can't find token (res={res2}, url={res2.url})")

    token = token_container["value"]

    files = {"btn-upload-format": open(azw3_path, "rb")}
    data = {"csrf_token": token}

    res3 = session.post(URL + f"/admin/book/{book_id}", files=files, data=data)
    res3.raise_for_status()

    ebook_path.unlink()
    azw3_path.unlink()


def update_books():
    print(f"Updating books with force={FORCE_CONVERSION}")
    login()
    ids = get_books()
    for book_id in ids:
        process_book(book_id, force=FORCE_CONVERSION)
