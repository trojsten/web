FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual build-deps gcc g++ make libffi-dev musl-dev postgresql-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev librsvg

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

RUN pip install "gunicorn<19.8"

COPY ./requirements3.devel.txt /web/requirements3.devel.txt
WORKDIR /web

RUN pip install --no-cache-dir -r requirements3.devel.txt

COPY . /web

RUN python manage.py compilemessages

ENV GUNICORN_WORKERS 2

CMD gunicorn --bind 0.0.0.0:80 --workers=${GUNICORN_WORKERS} --reload trojsten.wsgi:application
