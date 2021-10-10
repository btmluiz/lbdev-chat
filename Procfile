release: python manage.py migrate
web: daphne lbdev_chat.asgi:application --port $PORT --bind 0.0.0.0 -v2