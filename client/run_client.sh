#!/bin/bash

mkdir -p /code/client/src/locales &&
node ./build_locale/CreateLocaleJson.js &&
echo "$DEV_MODE"
if [ "$DEV_MODE" == "true" ]; then
  echo 'dev mode'
  npm run serve
else
  echo 'not dev mode'
  npm  run build
fi
