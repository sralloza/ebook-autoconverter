#!/usr/bin/env python3

import asyncio
from typing import List

import click
import httpx
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8083"
# https://books.sralloza.es/get_authors_json?q=author


class BooksUploader:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.logged_in = False

    def parse_res_for_csrf_token(self, res: httpx.Response) -> str:
        soup = BeautifulSoup(res.text, "html.parser")
        csrf_token_container = soup.find("input", {"name": "csrf_token"})
        if csrf_token_container is None:
            raise ValueError("Could not find csrf_token in response")
        return csrf_token_container["value"]

    async def login(self):
        if self.logged_in:
            return

        res = await self.client.get("/login")
        res.raise_for_status()
        csrf_token = self.parse_res_for_csrf_token(res)

        res = await self.client.post(
            url="/login",
            data={
                "csrf_token": csrf_token,
                "username": "admin",
                "password": "admin123",
                "next": "/"
            },
            follow_redirects=True,
        )
        res.raise_for_status()
        self.logged_in = True

    async def upload_book(self, book_path: str):
        await self.login()
        res = await self.client.get("")
        csrf_token = self.parse_res_for_csrf_token(res)

        res = await self.client.post(
            url="/upload",
            files={"btn-upload": open(book_path, "rb")},
            data={"csrf_token": csrf_token},
        )
        res.raise_for_status()

async def main(book_paths: List[str]):
    async with httpx.AsyncClient(timeout=100, base_url=BASE_URL) as client:
        books_uploader = BooksUploader(client)
        for book_path in book_paths:
            await books_uploader.upload_book(book_path)


@click.command()
@click.argument("book_paths", nargs=-1)
def cli(book_paths: List[str]):
    asyncio.run(main(book_paths))


if __name__ == "__main__":
    cli()
