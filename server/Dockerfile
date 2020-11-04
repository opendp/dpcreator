FROM python:3
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

# Run requirements
COPY requirements/ /code/requirements
RUN pip install -r requirements/dev.txt

COPY . /code/


