# Ebook Autoconverter

Script that converts all `epub` ebooks saved in a [calibre web](https://docs.linuxserver.io/images/docker-calibre-web) server to `azw3` (Kindle) and sends them back to the [calibre web](https://docs.linuxserver.io/images/docker-calibre-web) server.

In order to run it, the following env vars must be set:

- `CALIBRE_WEB_URL`: full [calibre web](https://docs.linuxserver.io/images/docker-calibre-web) URL (like `https://google.es`).
- `CALIBRE_WEB_USERNAME`: [calibre web](https://docs.linuxserver.io/images/docker-calibre-web) admin username.
- `CALIBRE_WEB_PASSWORD`: [calibre web](https://docs.linuxserver.io/images/docker-calibre-web) admin password.

There are others optional env vars:

- `FORCE_CONVERSION`: if `true` the script will convert and update **all** books, not just the ones without an `azw3` version.

## Development

### Build image

```shell
docker build -t sralloza/ebook-autoconverter:$VERSION .
docker push sralloza/ebook-autoconverter:$VERSION
```

## Run container

Using `-e` flags:

```shell
docker run --rm -e CALIBRE_WEB_URL=XXXXX -e CALIBRE_WEB_USERNAME=USER -e CALIBRE_WEB_PASSWORD=PASSWORD sralloza/ebook-autoconverter:$VERSION
```

Using `.env` file:

```shell
docker run --rm --env-file .env sralloza/ebook-autoconverter:$VERSION
```

`.env` contents:

```text
CALIBRE_WEB_URL=http://127.0.0.1
CALIBRE_WEB_USERNAME=admin
CALIBRE_WEB_PASSWORD=admin123
```
