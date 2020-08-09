FROM python:rc-alpine
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY start.sh /app/start.sh
RUN pip install --no-cache -r /app/requirements.txt && apk add --no-cache nginx && chmod u+x start.sh
COPY src /app
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD "/app/start.sh"