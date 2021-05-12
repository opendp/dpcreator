FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/opendp/opendp-ux

ENV PYTHONUNBUFFERED=1

# -------------------------------------
# Copy over the requirements and run them
# -------------------------------------
RUN mkdir -p /code/server
WORKDIR /code/server
COPY ./requirements/ ./requirements
RUN pip install --no-cache-dir -r requirements/dev.txt
#RUN pip3 install --no-cache-dir -r requirements/prod.txt

# -------------------------------------
# Copy over the rest of the repository
# -------------------------------------
#RUN mkdir /code
WORKDIR /code
COPY . /code/server
WORKDIR /code/server

#RUN pip install -r requirements/dev.txt
