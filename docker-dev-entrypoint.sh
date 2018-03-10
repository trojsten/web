socat TCP4-LISTEN:8047,reuseaddr,fork TCP4:login:8047 &
python manage.py runserver 0.0.0.0:8000
