FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED=0

RUN apk add --no-cache --virtual build-deps gcc g++ make libffi-dev musl-dev postgresql-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev

COPY . /web
WORKDIR /web

RUN pip install pip-tools; \
	pip-compile requirements.in requirements.devel.in -o requirements.txt; \
	pip install -r requirements.txt; \
        python manage.py compilemessages

CMD python manage.py runserver 0.0.0.0:8000
