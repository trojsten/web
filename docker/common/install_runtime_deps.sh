#!/bin/sh
apk add --update --no-cache --virtual runtime-deps \
    freetype \
    fribidi \
    gettext \
    harfbuzz \
    jpeg \
    lcms2 \
    libpq \
    librsvg \
    musl \
    openjpeg \
    tcl \
    tiff \
    tk \
    zlib \
    libmagic
