FROM python:3.8-alpine3.12

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev \
        gcc

RUN pip install --upgrade pip
RUN pip install poetry

RUN apk del \
        libressl-dev \
        musl-dev \
        libffi-dev \
        gcc

COPY ./docker/common /tmp/build

RUN set -x \
    && sh /tmp/build/install_build_deps.sh \
    && sh /tmp/build/install_runtime_deps.sh \
    && pip install black

COPY ./fonts/* /usr/share/fonts/

RUN fc-cache -f -v
