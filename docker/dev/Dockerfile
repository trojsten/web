FROM python:3.7-alpine3.10

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache curl

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python /dev/stdin -p \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

COPY ./docker/common /tmp/build

RUN set -x \
    && sh /tmp/build/install_build_deps.sh \
    && sh /tmp/build/install_runtime_deps.sh

COPY ./fonts/* /usr/share/fonts/

RUN fc-cache -f -v

COPY . /web

WORKDIR /web

RUN poetry config virtualenvs.create false && \
    poetry install -n

RUN python manage.py compilemessages

CMD python manage.py runserver 0.0.0.0:8000
