FROM python:2.7

RUN mkdir /app
WORKDIR /app

COPY main.py .
COPY LICENSE .
COPY requirements.txt .

COPY Core Core
COPY Plugins Plugins

RUN pip install -r requirements.txt

CMD python main.py