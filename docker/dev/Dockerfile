FROM python:3.8-alpine3.11

ENV PYTHONUNBUFFERED=0 \
    GET_POETRY_IGNORE_DEPRECATION=1

RUN apk add --no-cache curl

COPY ./docker/common/ /tmp/build/

RUN set -x \
    && sh /tmp/build/install_build_deps.sh \
    && sh /tmp/build/install_runtime_deps.sh
    
RUN curl -sSL https://install.python-poetry.org | python - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY ./fonts/* /usr/share/fonts/

RUN fc-cache -f -v

# Fix pip version to a known working one (source image often gets re-released when new pip
# gets released, but is cached locally, this can cause problems for new developers and deploys
# that are non-trivial to debug)
RUN pip install pip==20.0.2

COPY ./pyproject.toml /install/
COPY ./poetry.lock /install/

WORKDIR /install

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# We will mount source directory to /web
WORKDIR /web

CMD python manage.py compilemessages && python manage.py runserver 0.0.0.0:8000
