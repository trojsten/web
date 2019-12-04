FROM python:3.7-alpine3.10 AS base

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual common-deps curl

FROM base AS builder
# Install prerelease poetry

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python /dev/stdin -p \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY . /tmp/build

WORKDIR /tmp/build

RUN set -x \
    && poetry export -f requirements.txt > requirements.txt


FROM base AS installer

COPY ./docker/common/install_build_deps /tmp/build

RUN set -x \
    && sh /tmp/build/install_build_deps.sh

COPY --from=builder /tmp/build/requirements.txt /
RUN set -x \
    && pip install --root /install --no-warn-script-location -r requirements.txt


FROM base

COPY ./docker/common/install_runtime_deps /tmp/build

# These are not strictly dependencies of trojsten-web, but are required for production
RUN set -x \
    && pip install --no-cache-dir 'gunicorn<20' \
    && apk add nginx \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && sh /tmp/build/install_runtime_deps.sh \
    \
    # Clean up
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/build

COPY ./docker/prod/nginx/staticfiles.conf /etc/nginx/conf.d/default.conf

COPY --from=installer /install /

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

COPY ./manage.py /web/manage.py
COPY ./trojsten /web/trojsten

WORKDIR /web

ENV TROJSTENWEB_STATIC_ROOT=/static
ENV DJANGO_SETTINGS_MODULE=trojsten.settings.production
RUN python manage.py collectstatic --noinput

ENV GUNICORN_WORKERS 2
ENV GUNICORN_HOST 0.0.0.0:80
CMD gunicorn --bind ${GUNICORN_HOST} --workers=${GUNICORN_WORKERS} trojsten.wsgi:application

STOPSIGNAL SIGHUP
HEALTHCHECK CMD curl -fIsS http://localhost:8000/ || exit 1
EXPOSE 3031 8080
