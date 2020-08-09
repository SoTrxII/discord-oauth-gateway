gunicorn --bind 0.0.0.0:5000 wsgi:app&
nginx -g "pid /tmp/nginx.pid; daemon off;"
