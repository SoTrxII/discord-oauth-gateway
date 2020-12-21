gunicorn --bind 0.0.0.0:5000 wsgi:app&
cp /etc/nginx/conf.d/default.conf /tmp.conf
envsubst '\$CORS_DOMAIN_REGEX' < /tmp.conf > /etc/nginx/conf.d/default.conf
rm /tmp.conf
nginx -g "pid /tmp/nginx.pid; daemon off;"
