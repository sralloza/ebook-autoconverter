#!/usr/bin/env bash

set -e

echo "+Cleaning data"
git clean -fdx test/data

echo "+Running pre-provision"
python test/pre-provision.py
echo "+Starting calibre-web"
docker-compose up -d calibre-web


function close() {
  echo "+Stopping all containers"
  docker-compose down
}

trap close EXIT
trap close ERR
trap close SIGINT
trap close SIGTERM
trap close SIGQUIT
trap close SIGKILL
trap close SIGSTOP

sleep 5
image=$(docker inspect --format='{{.Config.Image}}' calibre-web)
echo "+Calibre-web image: $image"

echo "+Uploading test.epub"
python test/upload_file.py test/test.epub

echo "+Building ebook-autoconverter"
docker-compose build app
echo "+Running ebook-autoconverter"
docker-compose run app


echo "+Firing curls"
curl -sv http://localhost:8083/download/1/epub/1.epub -o /tmp/1.epub --fail-with-body
curl -sv http://localhost:8083/download/1/azw3/1.azw3 -o /tmp/1.azw3 --fail-with-body
