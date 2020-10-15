FROM python:3
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

# Ensure newer version of Node
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN set -ex \
    && BUILD_DEPS="nodejs" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

COPY server /code/
COPY server/requirements/base.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY client /code/


