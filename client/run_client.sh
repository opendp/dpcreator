#!/bin/bash

printf "\n-- (10) Make dir: /code/client/src/locales"
mkdir -p /code/client/src/locales

printf "\n-- (20) Run CreateLocaleJson.js "
node ./build_locale/CreateLocaleJson.js 

printf "\n-- (30) 'npm run server --quiet' "
# npm run serve --quiet
