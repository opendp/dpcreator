#!/bin/bash

docker-compose rm -s -f db
docker-compose up -d --force-recreate --build db
docker-compose run --rm server ./migrate.sh
