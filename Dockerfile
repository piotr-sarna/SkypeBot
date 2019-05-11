FROM python:3.7-alpine

RUN mkdir /app
WORKDIR /app

COPY main.py .
COPY version.py .
COPY LICENSE .
COPY requirements.txt .

COPY Core Core
COPY Plugins Plugins

RUN apk add --no-cache build-base jpeg-dev zlib-dev
RUN LIBRARY_PATH=/lib:/usr/lib pip3 install -r requirements.txt

CMD python main.py