FROM python:3.7-slim-buster
COPY ./server .
COPY ./server/migrate.sh .
ENTRYPOINT []

# By default run entrypoint.sh, but if command-line arguments
# are given run those instead:
CMD ["./migrate.sh"]
