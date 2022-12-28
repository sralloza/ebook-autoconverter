"""Core module."""

import shutil
from pathlib import Path
from shutil import which
from typing import List

from bs4 import BeautifulSoup
from requests import Response, Session
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from .calibre import convert_ebook
from .config import settings
from .report import Report


class EbookAutoconverter:
    def __init__(self):
        self._driver: webdriver.Firefox | None = None
        self.session = Session()
        self.session.headers.update({"User-Agent": "ebook-autoconverter"})

    @property
    def driver(self) -> webdriver.Firefox:
        return self._driver

    def load_webdriver(self):
        if self._driver is None:
            options = Options()
            options.headless = True

            path = (
                "geckodriver"
                if which("geckodriver")
                else GeckoDriverManager().install()
            )
            self._driver = webdriver.Firefox(options=options, executable_path=path)
            self.login()

    def login(self):
        """Logs in calibre-web."""
        self.driver.get(settings.calibre_web_url + "/login")
        self.driver.find_element("id", "username").send_keys(
            settings.calibre_web_username
        )
        self.driver.find_element("id", "password").send_keys(
            settings.calibre_web_password
        )
        self.driver.find_element("name", "submit").click()
        if self.driver.current_url == settings.calibre_web_url + "/login":
            raise ValueError(f"Login failed: {self.driver.current_url!r}")

    def logout(self):
        """Logs out of calibre-web."""
        if self._driver:
            self.driver.get(settings.calibre_web_url + "/logout")
            if self.driver.current_url != settings.calibre_web_url + "/login":
                raise ValueError(f"Logout failed: {self.driver.current_url!r}")

    def upload_book(self, book_id: int, azw3_path: str):
        """Uploads a book to calibre-web."""
        self.load_webdriver()
        self.driver.get(settings.calibre_web_url + f"/admin/book/{book_id}")
        self.driver.find_element("id", "btn-upload-format").send_keys(azw3_path)
        self.clear_empty_identifier_types_in_form()
        self.driver.find_element("id", "submit").click()
        element_present = expected_conditions.presence_of_element_located(
            ("id", "title")
        )
        WebDriverWait(self.driver, 20).until(element_present)

    def clear_empty_identifier_types_in_form(self):
        identifiers_table = self.driver.find_element("id", "identifier-table")
        rows = identifiers_table.find_elements("tag name", "tr")
        for row in rows:
            identifier_type = row.find_element(
                "class name", "form-control"
            ).get_attribute("value")
            if not identifier_type:
                print("Removing identifier empty identifier")
                row.find_element("class name", "btn-default").click()

    def check_missing_convertions(self) -> bool:
        """Returns true if the number of files in each format are not equal."""

        res = self.session.get(settings.calibre_web_url + "/formats")
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        row_cont = soup.find(id="list")

        format_report = {}

        for row in row_cont.find_all(class_="row"):
            count = int(row.find("span").get_text(strip=True))
            fmt = row.find("a").get_text(strip=True)

            format_report[fmt] = count

        print(f"Format report: {format_report}")
        if not format_report:
            return False
        Report.books_total = max(format_report.values())
        if len(format_report.keys()) < 2:
            return True
        return len(set(format_report.values())) > 1

    def get_missing_converted_ebooks(self) -> list[int]:
        epub_ids = self.get_books("/formats/stored/epub")
        azw3_ids = self.get_books("/formats/stored/azw3")
        return list(set(epub_ids) - set(azw3_ids))

    def get_books(self, path: str) -> list[int]:
        """Returns the book IDs found."""

        res = self.session.get(settings.calibre_web_url + path)
        if res.status_code == 404:
            return []

        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        pags = soup.find("div", {"class": "pagination"})
        if pags is None:
            ids = self.find_books(res)
            ids.sort()
            print(f"Found {len(ids)} books in {path} (no pages): {ids}")
            return ids

        pages = set()
        for link in pags.find_all("a"):
            pages.add(link["href"])

        if len(pages) > 1:
            ids = []
            for link in pages:
                res_extra = self.session.get(settings.calibre_web_url + link)
                res_extra.raise_for_status()
                ids += self.find_books(res_extra)
        else:
            ids = self.find_books(res)

        ids.sort()
        print(f"Found {len(ids)} books in {path} ({len(pages)} pages): {ids}")
        return ids

    @staticmethod
    def find_books(res: Response) -> List[int]:
        """Finds all the book IDs given an HTTP response."""

        soup = BeautifulSoup(res.text, "html.parser")
        covers = soup.find_all("div", {"class": "meta"})
        links = []
        for cover in covers:
            links.append(cover.a["href"])

        ids = [int(x.split("/")[-1]) for x in links]
        return ids

    def check_format_exists(self, book_id: int, fmt: str) -> bool:
        """Returns true if the format exists."""

        res = self.session.head(
            settings.calibre_web_url + f"/download/{book_id}/{fmt}/x"
        )
        return res.status_code == 200

    def convert_and_upload_book(self, book_id: int):
        """Converts and uploads a book using the calibre executable."""

        ebook_path = Path(f"/tmp/ebook_autoconverter/book-{book_id}.epub")
        folder = ebook_path.parent
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True, exist_ok=True)
        res1 = self.session.get(
            settings.calibre_web_url + f"/download/{book_id}/epub/x"
        )
        res1.raise_for_status()
        ebook_path.write_bytes(res1.content)

        azw3_path = convert_ebook(ebook_path.as_posix())
        # azw3_path = ebook_path.with_suffix(".azw3")

        self.upload_book(book_id, azw3_path.as_posix())

        if not self.check_format_exists(book_id, "azw3"):
            raise ValueError(f"Upload failed silently for book {book_id}")

        ebook_path.unlink()
        azw3_path.unlink()

    @classmethod
    def update_books(cls):
        """Ensure all books are converted."""

        self = cls()
        print("Updating books")

        if self.check_missing_convertions():
            ids = self.get_missing_converted_ebooks()
            print(f"Missing convertions: {ids}")
            for book_id in ids:
                self.convert_and_upload_book(book_id)
                Report.books_converted += 1
        else:
            print("No missing convertions")

        Report.print_report()
        self.logout()
