FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual build-deps gcc g++ make libffi-dev musl-dev postgresql-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev librsvg

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

COPY ./requirements.txt /web/requirements.txt
WORKDIR /web

RUN pip install --no-cache-dir -r requirements.txt

COPY . /web

RUN python manage.py compilemessages

CMD python manage.py runserver 0.0.0.0:8000
