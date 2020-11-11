FROM python:3
ENV PYTHONUNBUFFERED=1

# This is a development API key, which allows for sending emails
# and does not grant any other permissions to the SendGrid account
ENV SENDGRID_API_KEY=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

RUN mkdir /code
WORKDIR /code

COPY . /code/server
WORKDIR /code/server

RUN pip install -r requirements/base.txt

