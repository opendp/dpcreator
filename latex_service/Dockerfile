# Base image includes Python 3.9 and TeX Live package
FROM ghcr.io/opendp/dpcreator/texlive-base:latest

MAINTAINER OpenDP https://github.com/opendp

LABEL organization="OpenDP" \
      version="0.1-alpha" \
      release-date="2022-10-14" \
      description="DP Creator LaTeX service"

# -------------------------------------
# Copy over the requirements and run them
# -------------------------------------
RUN mkdir -p /code/latex_service
WORKDIR /code/latex_service
COPY ./requirements/ ./requirements
RUN pip install --no-cache-dir -r requirements/dev.txt

# -------------------------------------
# Copy over the rest of the repository
# -------------------------------------
WORKDIR /code
COPY . /code/latex_service
WORKDIR /code/latex_service
