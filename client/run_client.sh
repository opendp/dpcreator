#!/bin/bash

mkdir -p /code/client/src/locales &&
node ./build_locale/CreateLocaleJson.js &&
npm run serve --quiet