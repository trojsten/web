FROM python:3.7-alpine3.10 AS web

ENV PYTHONUNBUFFERED=0

RUN set -x \
    \
    # Build dependencies
    && apk add --update --no-cache \
    curl \
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

# Install prerelease poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python /dev/stdin -p \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY . /web

WORKDIR /web

RUN set -x \
    && poetry export -f requirements.txt > requirements.txt

RUN set -x \
    && pip install -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=trojsten.settings.production
ENV TROJSTENWEB_STATIC_ROOT=/static
# These  are required non empty by the produvtion settings module.
ENV TROJSTENWEB_LOGIN_KEY=unused_key
ENV TROJSTENWEB_LOGIN_SECRET=unused_secret

RUN python manage.py collectstatic --noinput

FROM nginx:1.17-alpine

COPY --from=web /static /static

COPY ./docker/prod/nginx/staticfiles.conf /etc/nginx/conf.d/default.conf
