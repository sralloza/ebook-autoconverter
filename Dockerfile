FROM linuxserver/calibre

ENV GET_POETRY https://install.python-poetry.org
ENV POETRY_VIRTUALENVS_CREATE=false

RUN apt update && \
    apt upgrade -y && \
    apt install -y python3-pip

WORKDIR /code

# Install Poetry
RUN curl -sSL ${GET_POETRY} | POETRY_HOME=/opt/poetry python3 && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

COPY ./pyproject.toml ./poetry.lock* /code/

RUN poetry install --no-dev

COPY ebook_autoconverter /code/ebook_autoconverter/

RUN poetry install --no-dev

ENTRYPOINT [ "python3", "-m", "ebook_autoconverter" ]
