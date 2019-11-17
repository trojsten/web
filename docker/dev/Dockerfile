FROM trojsten/web-base:latest

RUN ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

ENV PYTHONUNBUFFERED=0

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

COPY . /web

WORKDIR /web

RUN poetry config settings.virtualenvs.create false && \
    poetry install -n

RUN python manage.py compilemessages

CMD python manage.py runserver 0.0.0.0:8000
