FROM trojsten/web-base:latest

ENV PYTHONUNBUFFERED=0

COPY ./fonts/* /usr/share/fonts/
RUN fc-cache -f -v

COPY ./requirements.txt /web/requirements.txt
WORKDIR /web

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /web

RUN python manage.py compilemessages

CMD python manage.py runserver 0.0.0.0:8000
