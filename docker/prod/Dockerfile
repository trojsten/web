FROM python:3.8-alpine3.11 AS base

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual common-deps curl

FROM base AS builder

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY ./pyproject.toml /tmp/build/
COPY ./poetry.lock /tmp/build/

WORKDIR /tmp/build/

RUN set -x \
    && poetry export -f requirements.txt > requirements.txt


FROM base AS installer

COPY ./docker/common/install_build_deps.sh /tmp/build/

RUN set -x \
    && sh /tmp/build/install_build_deps.sh

WORKDIR /
COPY --from=builder /tmp/build/requirements.txt /
# Explanation of flags:
#
#   - `--ignore-installed`: If a package is installed locally, it wouldn't get installed to the alternate root.
#     This options ignores locally-installed packages, ensuring that all packages are installed to the alternate root.
#   - `--no-compile`: Don't write Python bytecode (smaller image size)
#   - `--no-deps`: Don't resolve dependencies. In first invocation dependency resolution should be completely
#     unnecessary, since the file should contain locked versions of all needed dependencies.
#     In the second invocation dependency resolution is outright harmful, since wheels that will be built as part
#     of the install process will contain version constraints from `pyproject.toml`, not from `poetry.lock` - so we
#     may end up installing a newer version of dependency than the one specified in our lock file.
#     (moreover, if a project contains local dependencies, the resulting wheel will have invalid METADATA and the
#     install would fail - https://github.com/python-poetry/poetry/issues/3148.)
#   - `--no-warn-script-location`: Don't generate warnings that destination for script executables is not in $PATH.
#     That's expected since we are installing to a different root.
#   - `--root`: Install everything to this alternate root directory - we will later copy it to the real root
#     in the final stage, leaving all build dependencies behind.
RUN pip install -r requirements.txt --ignore-installed --no-compile --no-deps --no-warn-script-location --root /install


FROM base

COPY ./docker/common/install_runtime_deps.sh /tmp/build/

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
RUN python manage.py compilemessages

ENV GUNICORN_WORKERS 2
ENV GUNICORN_HOST 0.0.0.0:80

COPY ./docker/prod/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]

# STOPSIGNAL SIGHUP
# HEALTHCHECK CMD curl -fIsS http://localhost:80/ || exit 1
EXPOSE 80
