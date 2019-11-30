FROM python:3.7-alpine3.10 AS base

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual common-deps curl

FROM base AS builder
# Install prerelease poetry

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python /dev/stdin -p \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY . /tmp/build
RUN set -x \
    && cd /tmp/build \
    && poetry export -f requirements.txt > requirements.txt

FROM base AS installer

RUN set -x \
    \
    # Build dependencies
    && apk add --update --no-cache \
    freetype-dev \
    fribidi-dev \
    gcc \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    libffi-dev \
    musl-dev \
    openjpeg-dev \
    postgresql-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev \
    && rm -rf /var/cache/apk/*

COPY --from=builder /tmp/build/requirements.txt /
RUN set -x \
    && pip install --root /install --no-warn-script-location -r requirements.txt

FROM base

# These are not strictly dependencies of trojsten-web, but are required for production
RUN pip install --no-cache-dir 'gunicorn<20'

RUN set -x \
    \
    # Runtime dependencies
    && apk add --update --no-cache \
    freetype \
    fribidi \
    gettext \
    harfbuzz \
    jpeg \
    lcms2 \
    libpq \
    musl \
    openjpeg \
    tcl \
    tiff \
    tk \
    zlib \
    \
    # Clean up
    && rm -rf /var/cache/apk/*

COPY --from=installer /install /

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

COPY ./manage.py /web/manage.py
COPY ./trojsten /web/trojsten

WORKDIR /web

ENV GUNICORN_WORKERS 2
ENV GUNICORN_HOST 0.0.0.0:80
CMD gunicorn --bind ${GUNICORN_HOST} --workers=${GUNICORN_WORKERS} trojsten.wsgi:application

STOPSIGNAL SIGHUP
HEALTHCHECK CMD curl -fIsS http://localhost:8000/ || exit 1
EXPOSE 3031 8080
