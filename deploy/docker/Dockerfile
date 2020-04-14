FROM python:3.7.3-slim-stretch

RUN apt-get update && apt-get install -y gcc libmariadbclient-dev-compat \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip3 install uwsgi

COPY app /app
COPY asset/uwsgi.ini /etc/uwsgi.ini

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["uwsgi",  "-i",  "/etc/uwsgi.ini"]
EXPOSE 8000
