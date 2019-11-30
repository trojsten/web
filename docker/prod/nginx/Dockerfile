FROM python:3.7-alpine3.10 AS builder

RUN apk add --no-cache curl

# Install prerelease poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python /dev/stdin -p \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY . /build

WORKDIR /build

RUN set -x \
    && poetry export -f requirements.txt > requirements.txt

FROM python:3.7-alpine3.10 AS web

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

COPY --from=builder /build/requirements.txt /tmp/build/requirements.txt

RUN set -x \
    && pip install -r /tmp/build/requirements.txt

COPY ./trojsten /web/trojsten
COPY ./manage.py /web/manage.py

WORKDIR /web

ENV DJANGO_SETTINGS_MODULE=trojsten.settings.production
ENV TROJSTENWEB_STATIC_ROOT=/static

RUN python manage.py collectstatic --noinput

FROM nginx:1.17-alpine

COPY --from=web /static /static

COPY ./docker/prod/nginx/staticfiles.conf /etc/nginx/conf.d/default.conf
