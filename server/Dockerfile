FROM python:3
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY . /code/
COPY requirements/base.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY migrate.sh /code/server/
RUN chmod 777 /code/server/migrate.sh
