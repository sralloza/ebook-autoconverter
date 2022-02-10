FROM linuxserver/calibre

ENV GET_POETRY https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py


RUN apt update && \
    apt upgrade -y && \
    apt install -y python3-pip

WORKDIR /code

# Install Poetry
RUN curl -sSL ${GET_POETRY} | POETRY_HOME=/opt/poetry python3 && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /code/

RUN poetry install --no-dev

COPY ebook_autoconverter /code/ebook_autoconverter/

RUN poetry install --no-dev

ENTRYPOINT [ "python3" ]
CMD [ "-m", "ebook_autoconverter" ]
