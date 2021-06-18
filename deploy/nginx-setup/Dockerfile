FROM nginx:1.20

MAINTAINER OpenDP http://opendp.org
LABEL organization="OpenDP" \
      2ra.vn.version="0.1-alpha" \
      2ra.vn.release-date="2021-05-17" \
      description="Nginx for DPCreator"

# -----------------------------------
# Use template that has placeholders for
# environment variables.
# -----------------------------------
COPY nginx.conf.template /etc/nginx/templates/

# -----------------------------------
# Set environment variables
#
# NGINX_MAX_UPLOAD_SIZE - Set the maximum upload size for files
# NGINX_SERVER_NAME - Set the server name.  Note ".dpcreator.org" may be used for
#                     2ravens.org, cyan.dpcreator.org, blue.dpcreator.org, etc.
#
# -----------------------------------
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/ \
    NGINX_MAX_UPLOAD_SIZE=20M \
    NGINX_SERVER_NAME=.dpcreator.org


# -----------------------------------
# When the container is run, it executes a function which reads template
# files in /etc/nginx/templates/*.template and outputs the result of
# executing envsubst to /etc/nginx/conf.d.
# ref: "Using environment variables in nginx configuration (new in 1.19)"
#   - https://hub.docker.com/_/nginx
# -----------------------------------
