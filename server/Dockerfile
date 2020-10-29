FROM python:3
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY . /code/server
WORKDIR /code/server

RUN pip install -r requirements/base.txt
