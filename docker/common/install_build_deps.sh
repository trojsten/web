#!/bin/sh
apk add --update --no-cache --virtual build-deps \
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
    zlib-dev
