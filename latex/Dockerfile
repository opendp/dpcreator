FROM python:3.9

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
  texlive-full
# -------------------------------------
# Copy over the requirements and run them
# -------------------------------------
RUN mkdir -p /code/latex
WORKDIR /code/latex
COPY ./requirements/ ./requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

# -------------------------------------
# Copy over the rest of the repository
# -------------------------------------
WORKDIR /code
COPY . /code/latex
WORKDIR /code/latex
